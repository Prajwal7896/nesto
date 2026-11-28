import ezdxf
from types import SimpleNamespace

from backend.api.rag.layout_validator import validate_layout
from backend.api.rag.renderer.exporter import Exporter
from backend.api.rag.renderer.geometry.point import Point
from backend.api.rag.renderer.wall_generator import WallGenerator
from backend.api.rag.renderer.door_generator import DoorGenerator
from backend.api.rag.renderer.window_generator import WindowGenerator
from backend.api.rag.renderer.staircase import StaircaseGenerator
from backend.api.rag.renderer.roof import RoofGenerator
from backend.api.rag.renderer.slab import SlabGenerator
from backend.api.rag.renderer.furniture import FurnitureGenerator
from backend.api.rag.renderer.dimensions import DimensionGenerator
from backend.api.rag.renderer.labels import LabelGenerator
from backend.api.rag.renderer.hatch import HatchGenerator
from backend.api.rag.renderer.symbols import SymbolLibrary

class Renderer:
    def __init__(self):
        self.doc = ezdxf.new("R2010")
        self.msp = self.doc.modelspace()

        self.exporter = Exporter(self.doc)
        self.wall_gen = WallGenerator(self.msp)
        self.door_gen = DoorGenerator(self.msp)
        self.window_gen = WindowGenerator(self.msp)
        self.stair_gen = StaircaseGenerator(self.msp)
        self.roof_gen = RoofGenerator(self.msp)
        self.slab_gen = SlabGenerator(self.msp)
        self.furniture_gen = FurnitureGenerator(self.msp)
        self.dim_gen = DimensionGenerator(self.msp)
        self.label_gen = LabelGenerator(self.msp)
        self.hatch_gen = HatchGenerator(self.msp)
        self.symbols = SymbolLibrary(self.msp)

    
    @staticmethod
    def _hex_to_rgb(color):
        color = str(color).strip().lstrip("#")

        if len(color) != 6:
            raise ValueError("Colors must use #RRGGBB format.")

        try:
            return int(color, 16)
        except ValueError as exc:
            raise ValueError(f"Invalid color: {color}") from exc

    def _set_layer_color(self, layer_name, color):
        rgb = self._hex_to_rgb(color)

        if layer_name in self.doc.layers:
            layer = self.doc.layers.get(layer_name)
        else:
            layer = self.doc.layers.new(layer_name)

        layer.dxf.true_color = rgb

    def _apply_customization(self, customization=None):

        customization = customization or {}

        layer_colors = {
            "WALLS": customization.get("wallColor", "#333333"),
            "DOORS": customization.get("doorColor", "#8B4513"),
            "WINDOWS": customization.get("windowColor", "#2196F3"),
            "HATCH": customization.get("floorColor", "#EEEEEE"),
            "FURNITURE": customization.get("accentColor", "#D4A373"),
            "LABELS": customization.get("accentColor", "#D4A373"),
        }

        for layer_name, color in layer_colors.items():
            self._set_layer_color(layer_name, color)

        return customization

    @staticmethod
    def _get_room_color(room_type, customization):
        room_type = str(room_type).lower().strip()

        color_mapping = {
            "living": "livingColor",
            "living room": "livingColor",
            "bedroom": "bedroomColor",
            "master bedroom": "bedroomColor",
            "guest bedroom": "bedroomColor",
            "kitchen": "kitchenColor",
            "dining": "floorColor",
            "bathroom": "floorColor",
            "toilet": "floorColor",
            "washroom": "floorColor",
        }

        color_key = color_mapping.get(room_type, "floorColor")

        return customization.get(color_key, "#EEEEEE")

    def _normalize_polygon(self, polygon):
        if hasattr(polygon, "vertices"):
            vertices = polygon.vertices
        else:
            vertices = polygon

        vertices = [
            point
            if isinstance(point, Point)
            else Point(float(point[0]), float(point[1]))
            for point in vertices
        ]

        from backend.api.rag.renderer.geometry.line import Line

        edges = [
            Line(vertices[i], vertices[(i + 1) % len(vertices)])
            for i in range(len(vertices))
        ] if len(vertices) >= 2 else []

        return SimpleNamespace(vertices=vertices, edges=edges)

    @staticmethod
    def _wall_coordinates(wall):
        start = wall["start"]
        end = wall["end"]

        if hasattr(start, "x"):
            start = (float(start.x), float(start.y))
        else:
            start = (float(start[0]), float(start[1]))

        if hasattr(end, "x"):
            end = (float(end.x), float(end.y))
        else:
            end = (float(end[0]), float(end[1]))

        return start, end

    @staticmethod
    def _opening_intervals(wall, openings):
        start, end = Renderer._wall_coordinates(wall)

        dx = end[0] - start[0]
        dy = end[1] - start[1]
        length = (dx * dx + dy * dy) ** 0.5

        if length <= 0:
            return []

        intervals = []

        for opening in openings:
            width = float(opening.get("width", 0))
            position = float(opening.get("position", 0.5))

            if width <= 0 or not 0 <= position <= 1:
                continue

            half = width / (2.0 * length)
            left = max(0.0, position - half)
            right = min(1.0, position + half)

            if right > left:
                intervals.append((left, right))

        intervals.sort()
        merged = []

        for left, right in intervals:
            if merged and left <= merged[-1][1]:
                merged[-1] = (
                    merged[-1][0],
                    max(merged[-1][1], right),
                )
            else:
                merged.append((left, right))

        return merged

    def _draw_wall_with_openings(self, wall, openings, layer="WALLS"):
        start, end = self._wall_coordinates(wall)
        dx = end[0] - start[0]
        dy = end[1] - start[1]

        intervals = self._opening_intervals(wall, openings)
        cursor = 0.0

        def point_at(t):
            return (
                start[0] + dx * t,
                start[1] + dy * t,
            )

        for left, right in intervals:
            if left > cursor:
                self.msp.add_line(
                    point_at(cursor),
                    point_at(left),
                    dxfattribs={"layer": layer},
                )
            cursor = max(cursor, right)

        if cursor < 1.0:
            self.msp.add_line(
                point_at(cursor),
                end,
                dxfattribs={"layer": layer},
            )

    def _draw_room_walls(self, rooms, doors, windows):
        wall_lookup = {}
        room_polygons = {}

        for room_index, room in enumerate(rooms):
            polygon = self._normalize_polygon(room.get("polygon", []))

            if len(polygon.vertices) < 3:
                print(
                    f"Skipping invalid room polygon: "
                    f"{room.get('id', room.get('type', 'unknown'))}"
                )
                continue

            room_polygons[room_index] = polygon
            vertices = polygon.vertices

            for edge_index in range(len(vertices)):
                start = vertices[edge_index]
                end = vertices[(edge_index + 1) % len(vertices)]

                wall = {
                    "start": start,
                    "end": end,
                }

                wall_id = room_index * 4 + edge_index
                wall_lookup[wall_id] = wall

        openings_by_wall = {}

        for opening in doors + windows:
            wall_id = opening.get("wall")

            if wall_id not in wall_lookup:
                print(f"Skipping opening with unresolved wall ID: {wall_id}")
                continue

            openings_by_wall.setdefault(wall_id, []).append(opening)

        for wall_id, wall in wall_lookup.items():
            self._draw_wall_with_openings(
                wall,
                openings_by_wall.get(wall_id, []),
            )

        return wall_lookup, room_polygons

    def _draw_opening_symbols(self, wall_lookup, doors, windows):
        for door in doors:
            wall = wall_lookup.get(door.get("wall"))

            if wall is None:
                continue

            try:
                self.door_gen.place_door_on_wall(
                    wall=wall,
                    position_t=float(door.get("position", 0.5)),
                    width=float(door.get("width", 900)),
                )
            except (TypeError, ValueError, KeyError, AttributeError) as exc:
                print(f"Could not draw door symbol: {exc}")

        for window in windows:
            wall = wall_lookup.get(window.get("wall"))

            if wall is None:
                continue

            try:
                self.window_gen.place_window_on_wall(
                    wall=wall,
                    position_t=float(window.get("position", 0.5)),
                    width=float(window.get("width", 1200)),
                )
            except (TypeError, ValueError, KeyError, AttributeError) as exc:
                print(f"Could not draw window symbol: {exc}")

    def render(
        self,
        layout: dict,
        prompt: str,
        user_id: str,
        base_name: str | None = None,
        customization: dict | None = None,
        prevalidated: bool = False,
    ):
        customization = self._apply_customization(customization)
        if not prevalidated:
            validation_layout = dict(layout)
            validation_layout["rooms"] = (
                layout.get("rooms", [])
                + layout.get("site_features", [])
                + layout.get("open_spaces", [])
            )

            validation = validate_layout(validation_layout)

            if not validation["valid"]:
                raise ValueError(
                    "Refusing to render an invalid layout: "
                    + "; ".join(validation["errors"])
                )

        rooms = layout.get("rooms", [])
        doors = layout.get("doors", [])
        windows = layout.get("windows", [])

        print("\n========== ROOMS ==========")

        for room in rooms:
            print(room.get("type"), room.get("polygon"))

        # Draw floor fills first so walls, furniture and labels
        # remain visible above the fills.
        room_polygons = {}

        for room_index, room in enumerate(rooms):

            polygon = self._normalize_polygon(
                room.get("polygon", [])
            )

            if len(polygon.vertices) < 3:
                continue

            room_polygons[room_index] = polygon

            room_type = room.get("type", "living")

            room_color = self._get_room_color(
                room_type,
                customization
            )

            self.hatch_gen.floor_hatch(
                polygon,
                layer="HATCH",
                color=room_color,
                pattern="SOLID",
            )

        wall_lookup, _ = self._draw_room_walls(
            rooms,
            doors,
            windows,
        )

        for feature in layout.get("site_features", []):
            polygon = self._normalize_polygon(feature.get("polygon", []))

            if len(polygon.vertices) < 3:
                raise ValueError(
                    f"Invalid geometry for site feature "
                    f"{feature.get('name', 'unknown')}."
                )

            self.wall_gen.generate_from_polygon(polygon)
            self.label_gen.add_room_label(
                polygon,
                feature.get("name", feature.get("type", "site feature")),
            )

        for area in layout.get("open_spaces", []):
            polygon = self._normalize_polygon(area.get("polygon", []))

            if len(polygon.vertices) < 3:
                raise ValueError(
                    f"Invalid geometry for open space "
                    f"{area.get('name', 'unknown')}."
                )

            self.msp.add_lwpolyline(
                [
                    (point.x, point.y)
                    for point in polygon.vertices
                ],
                close=True,
                dxfattribs={
                    "linetype": "DASHED",
                    "layer": "WALLS",
                },
            )

            self.label_gen.add_room_label(
                polygon,
                area.get("name", area.get("type", "open space")),
            )

        self._draw_opening_symbols(wall_lookup, doors, windows)

        for room_index, room in enumerate(rooms):
            polygon = room_polygons.get(room_index)

            if polygon is None:
                continue

            room_type = room.get("type", "living")

            self.furniture_gen.place_furniture(
                polygon,
                room_type,
            )

            self.label_gen.add_room_label(
                polygon,
                room.get("name", room_type),
            )

            self.label_gen.add_area_label(
                polygon,
                room.get("area", 0),
            )

        print("==========================\n")

        return self.exporter.export_all(
            base_name=base_name or f"floorplan_{user_id}",
            metadata={
                "prompt": prompt,
                "rooms": len(rooms),
            },
        )

    def render_2d(self, layout: dict, prompt: str, user_id: str):
        renderer = Renderer()
        return renderer.render(layout, prompt, user_id)
