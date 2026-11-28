"""Extract architectural geometry from Nesto's existing 2D planner output."""

from __future__ import annotations

from copy import deepcopy
from math import isfinite
from typing import Any, Dict, Iterable, List, Sequence, Tuple

from .scene_models import SceneFloor, SceneOpening, SceneRoom, SceneWall


class GeometryExtractor:
    """Translate planner dictionaries into typed floor, room, wall and opening data.

    Expected planner shape:
        {
            "floor": "ground_floor",
            "plot": {"width": ..., "height": ...},
            "rooms": [...],
            "site_features": [...],
            "open_spaces": [...],
            "doors": [{"wall": int, "position": 0..1, "width": ...}],
            "windows": [...],
            "floors": {"ground_floor": {...}, "first_floor": {...}}
        }

    All dimensions remain in millimetres in this layer.
    """

    def __init__(
        self,
        *,
        wall_height: float = 3000.0,
        wall_thickness: float = 150.0,
        door_height: float = 2100.0,
        window_height: float = 1200.0,
        window_sill_height: float = 900.0,
        floor_height: float = 3000.0,
    ) -> None:
        self.wall_height = self._positive(wall_height, "wall_height")
        self.wall_thickness = self._positive(wall_thickness, "wall_thickness")
        self.door_height = self._positive(door_height, "door_height")
        self.window_height = self._positive(window_height, "window_height")
        self.window_sill_height = self._non_negative(
            window_sill_height, "window_sill_height"
        )
        self.floor_height = self._positive(floor_height, "floor_height")

    def extract(self, layout: Dict[str, Any]) -> List[SceneFloor]:
        if not isinstance(layout, dict):
            raise TypeError("layout must be a dictionary produced by Nesto's planner.")

        floors_data = layout.get("floors")
        if isinstance(floors_data, dict) and floors_data:
            ordered = list(floors_data.items())
        else:
            floor_name = str(layout.get("floor") or "ground_floor")
            ordered = [(floor_name, layout)]

        result: List[SceneFloor] = []
        for floor_index, (floor_key, floor_data) in enumerate(ordered):
            if not isinstance(floor_data, dict):
                raise ValueError(f"Floor '{floor_key}' must contain a dictionary.")
            result.append(
                self._extract_floor(
                    str(floor_key),
                    floor_data,
                    floor_index=floor_index,
                )
            )
        return result

    def _extract_floor(
        self,
        floor_key: str,
        data: Dict[str, Any],
        *,
        floor_index: int,
    ) -> SceneFloor:
        plot = data.get("plot") or {}
        if not isinstance(plot, dict):
            raise ValueError(f"Floor '{floor_key}' has an invalid plot object.")

        plot_width = self._positive(plot.get("width"), f"{floor_key}.plot.width")
        plot_depth = self._positive(plot.get("height"), f"{floor_key}.plot.height")

        rooms = self._extract_room_collection(data.get("rooms", []), "room")
        features = self._extract_room_collection(
            data.get("site_features", []), "site_feature"
        )
        open_spaces = self._extract_room_collection(
            data.get("open_spaces", []), "open_space"
        )

        # Planner wall indices are room_index * 4 + edge_index, based on
        # the ordered `rooms` list. Preserve that exact contract.
        doors, windows = self._extract_openings(
            data.get("doors", []),
            data.get("windows", []),
            rooms,
        )

        all_walls: List[SceneWall] = []
        for room_index, room in enumerate(rooms):
            room.walls = self._build_walls(
                room,
                room_index,
                doors,
                windows,
            )
            all_walls.extend(room.walls)

        return SceneFloor(
            id=floor_key,
            name=floor_key.replace("_", " ").title(),
            elevation=floor_index * self.floor_height,
            plot_width=plot_width,
            plot_depth=plot_depth,
            rooms=rooms,
            site_features=features,
            open_spaces=open_spaces,
            walls=all_walls,
            doors=doors,
            windows=windows,
            connections=deepcopy(data.get("connections") or data.get("adjacency_graph") or []),
            structure=deepcopy(data.get("structure") or {}),
            engineering=deepcopy(data.get("engineering") or {}),
            metadata=deepcopy(data.get("metadata") or {}),
        )

    def _extract_room_collection(
        self,
        collection: Any,
        default_kind: str,
    ) -> List[SceneRoom]:
        if collection is None:
            return []
        if not isinstance(collection, list):
            raise ValueError(f"{default_kind} collection must be a list.")

        result = []
        for index, item in enumerate(collection):
            if not isinstance(item, dict):
                raise ValueError(f"{default_kind} at index {index} must be an object.")

            room_id = str(item.get("id") or f"{default_kind}_{index + 1}")
            room_type = str(item.get("type") or default_kind)
            x = self._number(item.get("x", 0.0), f"{room_id}.x")
            y = self._number(item.get("y", 0.0), f"{room_id}.y")
            width = self._positive(item.get("width"), f"{room_id}.width")
            depth = self._positive(item.get("height"), f"{room_id}.height")
            polygon = self._polygon(item.get("polygon"), x, y, width, depth, room_id)

            result.append(
                SceneRoom(
                    id=room_id,
                    type=room_type,
                    name=str(item.get("name") or room_type.replace("_", " ").title()),
                    x=x,
                    y=y,
                    width=width,
                    depth=depth,
                    area=self._non_negative(
                        item.get("area", width * depth), f"{room_id}.area"
                    ),
                    rotation=self._number(item.get("rotation", 0), f"{room_id}.rotation"),
                    polygon=polygon,
                    kind=str(item.get("kind") or default_kind),
                    source=deepcopy(item),
                )
            )
        return result

    def _extract_openings(
        self,
        doors_data: Any,
        windows_data: Any,
        rooms: List[SceneRoom],
    ) -> Tuple[List[SceneOpening], List[SceneOpening]]:
        doors = self._opening_collection(doors_data, "door", rooms)
        windows = self._opening_collection(windows_data, "window", rooms)
        return doors, windows

    def _opening_collection(
        self,
        collection: Any,
        kind: str,
        rooms: List[SceneRoom],
    ) -> List[SceneOpening]:
        if collection is None:
            return []
        if not isinstance(collection, list):
            raise ValueError(f"{kind} collection must be a list.")

        result: List[SceneOpening] = []
        for index, item in enumerate(collection):
            if not isinstance(item, dict):
                raise ValueError(f"{kind} at index {index} must be an object.")

            wall_index = item.get("wall")
            if not isinstance(wall_index, int) or isinstance(wall_index, bool) or wall_index < 0:
                raise ValueError(
                    f"{kind} at index {index} must have a non-negative integer wall index."
                )

            room_index, edge_index = divmod(wall_index, 4)
            if room_index >= len(rooms) or edge_index > 3:
                raise ValueError(
                    f"{kind} at index {index} references unresolved wall index {wall_index}."
                )

            position = self._number(item.get("position", 0.5), f"{kind}.position")
            if not 0.0 <= position <= 1.0:
                raise ValueError(f"{kind} position must be between 0 and 1.")

            width = self._positive(item.get("width"), f"{kind}.width")
            height = (
                self.door_height if kind == "door" else self.window_height
            )
            sill = 0.0 if kind == "door" else self.window_sill_height

            result.append(
                SceneOpening(
                    id=str(item.get("id") or f"{kind}_{index + 1}"),
                    kind=kind,
                    wall_id=f"{rooms[room_index].id}:wall:{edge_index}",
                    position=position,
                    width=width,
                    height=height,
                    sill_height=sill,
                    source_wall_index=wall_index,
                    source=deepcopy(item),
                )
            )
        return result

    def _build_walls(
        self,
        room: SceneRoom,
        room_index: int,
        doors: List[SceneOpening],
        windows: List[SceneOpening],
    ) -> List[SceneWall]:
        walls = []
        for edge_index, start in enumerate(room.polygon):
            end = room.polygon[(edge_index + 1) % len(room.polygon)]
            wall_id = f"{room.id}:wall:{edge_index}"
            attached = [
                opening
                for opening in doors + windows
                if opening.wall_id == wall_id
            ]
            walls.append(
                SceneWall(
                    id=wall_id,
                    room_id=room.id,
                    start=start,
                    end=end,
                    height=self.wall_height,
                    thickness=self.wall_thickness,
                    edge_index=edge_index,
                    openings=attached,
                    source={
                        "room_index": room_index,
                        "planner_wall_index": room_index * 4 + edge_index,
                    },
                )
            )
        return walls

    def _polygon(
        self,
        raw: Any,
        x: float,
        y: float,
        width: float,
        depth: float,
        room_id: str,
    ) -> List[Tuple[float, float]]:
        if raw is None:
            return [
                (x, y),
                (x + width, y),
                (x + width, y + depth),
                (x, y + depth),
            ]
        if not isinstance(raw, (list, tuple)) or len(raw) < 3:
            raise ValueError(f"{room_id}.polygon must contain at least three points.")

        vertices = []
        for index, point in enumerate(raw):
            if not isinstance(point, (list, tuple)) or len(point) < 2:
                raise ValueError(f"{room_id}.polygon[{index}] must contain x and y.")
            vertices.append(
                (
                    self._number(point[0], f"{room_id}.polygon[{index}].x"),
                    self._number(point[1], f"{room_id}.polygon[{index}].y"),
                )
            )
        return vertices

    @staticmethod
    def _number(value: Any, name: str) -> float:
        try:
            result = float(value)
        except (TypeError, ValueError) as exc:
            raise ValueError(f"{name} must be numeric.") from exc
        if not isfinite(result):
            raise ValueError(f"{name} must be finite.")
        return result

    @classmethod
    def _positive(cls, value: Any, name: str) -> float:
        result = cls._number(value, name)
        if result <= 0:
            raise ValueError(f"{name} must be greater than zero.")
        return result

    @classmethod
    def _non_negative(cls, value: Any, name: str) -> float:
        result = cls._number(value, name)
        if result < 0:
            raise ValueError(f"{name} cannot be negative.")
        return result
