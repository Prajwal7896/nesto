
from __future__ import annotations

from typing import Any


class WallGenerator:
    """Creates wall geometry specifications from room polygons.

    Coordinates and dimensions are in millimetres.
    Polygon points use [x, y], with vertical height represented separately.
    """

    def __init__(
        self,
        wall_height: float = 3000.0,
        wall_thickness: float = 150.0,
        exterior_thickness: float = 230.0,
    ):
        self.wall_height = self._positive(wall_height, "wall_height")
        self.wall_thickness = self._positive(
            wall_thickness, "wall_thickness"
        )
        self.exterior_thickness = self._positive(
            exterior_thickness, "exterior_thickness"
        )

    @staticmethod
    def _positive(value: float, name: str) -> float:
        value = float(value)
        if value <= 0:
            raise ValueError(f"{name} must be greater than zero")
        return value

    @staticmethod
    def _distance(a: list, b: list) -> float:
        return ((b[0] - a[0]) ** 2 + (b[1] - a[1]) ** 2) ** 0.5

    def generate(
        self,
        rooms: list[dict[str, Any]],
        floor_elevation: float = 0.0,
        exterior_room_ids: set[str] | None = None,
    ) -> list[dict[str, Any]]:
        if not isinstance(rooms, list):
            raise TypeError("rooms must be a list")

        exterior_room_ids = exterior_room_ids or set()
        walls = []

        for room_index, room in enumerate(rooms):
            room_id = str(room.get("id", f"room_{room_index}"))
            polygon = room.get("polygon")

            if not isinstance(polygon, list) or len(polygon) < 3:
                raise ValueError(
                    f"Room {room_id} must have a valid polygon"
                )

            for edge_index, start in enumerate(polygon):
                end = polygon[(edge_index + 1) % len(polygon)]

                if len(start) != 2 or len(end) != 2:
                    raise ValueError("Polygon points must contain x and y")

                length = self._distance(start, end)
                if length <= 0:
                    continue

                thickness = (
                    self.exterior_thickness
                    if room_id in exterior_room_ids
                    else self.wall_thickness
                )

                walls.append({
                    "id": f"{room_id}_wall_{edge_index}",
                    "room_id": room_id,
                    "wall_index": room_index * 4 + edge_index,
                    "edge_index": edge_index,
                    "start": [float(start[0]), float(start[1])],
                    "end": [float(end[0]), float(end[1])],
                    "length": length,
                    "height": self.wall_height,
                    "thickness": thickness,
                    "elevation": float(floor_elevation),
                    "type": (
                        "exterior"
                        if room_id in exterior_room_ids
                        else "interior"
                    ),
                    "openings": [],
                })

        return walls
