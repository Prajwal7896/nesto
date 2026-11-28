
import math
import ezdxf

from backend.api.rag.constraints import build_constraints
from backend.api.rag.planner import generate_layout
from backend.api.rag.optimizer import optimize
from backend.api.rag.layout_validator import validate
from backend.api.rag.renderer.exporter import Exporter

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
    def _valid_number(value):
        return (
            isinstance(value, (int, float))
            and not isinstance(value, bool)
            and math.isfinite(value)
        )

    @classmethod
    def _valid_point(cls, point):
        return (
            isinstance(point, (list, tuple))
            and len(point) >= 2
            and cls._valid_number(point[0])
            and cls._valid_number(point[1])
        )

    @classmethod
    def _valid_polygon(cls, polygon):
        if not isinstance(polygon, (list, tuple)) or len(polygon) < 3:
            return False

        return all(cls._valid_point(point) for point in polygon)

    @staticmethod
    def _failure(reason, details=None):
        result = {
            "status": "failed",
            "reason": reason,
        }

        if details is not None:
            result["details"] = details

        return result

    def _render_openings(self, openings, generator, default_width):
        rendered = 0
        skipped = []

        if not isinstance(openings, list):
            return {
                "rendered": 0,
                "skipped": ["Openings must be a list"],
            }

        for index, opening in enumerate(openings):
            if not isinstance(opening, dict):
                skipped.append(f"Opening {index}: invalid object")
                continue

            wall = opening.get("wall")
            position = opening.get("position", 0.5)
            width = opening.get("width", default_width)

            if (
                not isinstance(wall, int)
                or isinstance(wall, bool)
                or wall < 0
            ):
                skipped.append(f"Opening {index}: invalid wall index")
                continue

            if (
                not self._valid_number(position)
                or not 0 <= position <= 1
            ):
                skipped.append(f"Opening {index}: invalid position")
                continue

            if (
                not self._valid_number(width)
                or width <= 0
            ):
                skipped.append(f"Opening {index}: invalid width")
                continue

            try:
                if generator is self.door_gen:
                    generator.place_door_on_wall(
                        wall,
                        position,
                        width,
                    )
                else:
                    generator.place_window_on_wall(
                        wall,
                        position,
                        width,
                    )

                rendered += 1

            except (ValueError, TypeError, IndexError, KeyError) as exc:
                skipped.append(
                    f"Opening {index}: {type(exc).__name__}: {exc}"
                )

        return {
            "rendered": rendered,
            "skipped": skipped,
        }

    def _render_rooms(self, rooms):
        rendered = 0
        skipped = []

        for index, room in enumerate(rooms):
            if not isinstance(room, dict):
                skipped.append(f"Room {index}: invalid object")
                continue

            polygon = room.get("polygon")

            if not self._valid_polygon(polygon):
                skipped.append(f"Room {index}: invalid polygon")
                continue

            try:
                self.wall_gen.generate_from_polygon(polygon)
                rendered += 1
            except (ValueError, TypeError, IndexError, KeyError) as exc:
                skipped.append(
                    f"Room {index}: {type(exc).__name__}: {exc}"
                )

        return {
            "rendered": rendered,
            "skipped": skipped,
        }

    def _render_stairs(self, stairs):
        rendered = 0
        skipped = []

        if not isinstance(stairs, list):
            return {
                "rendered": 0,
                "skipped": ["Stairs must be a list"],
            }

        for index, stair in enumerate(stairs):
            if not isinstance(stair, dict):
                skipped.append(f"Stair {index}: invalid object")
                continue

            start = stair.get("start")
            end = stair.get("end")
            steps = stair.get("steps", 10)

            if not self._valid_point(start) or not self._valid_point(end):
                skipped.append(f"Stair {index}: invalid endpoints")
                continue

            if (
                not isinstance(steps, int)
                or isinstance(steps, bool)
                or steps < 1
            ):
                skipped.append(f"Stair {index}: invalid step count")
                continue

            try:
                self.stair_gen.create_straight_stair(
                    start,
                    end,
                    steps,
                )
                rendered += 1
            except (ValueError, TypeError, IndexError, KeyError) as exc:
                skipped.append(
                    f"Stair {index}: {type(exc).__name__}: {exc}"
                )

        return {
            "rendered": rendered,
            "skipped": skipped,
        }

    def render(self, prompt: str, user_id: str):
        if not isinstance(prompt, str) or not prompt.strip():
            return self._failure("Prompt must be a non-empty string")

        if not isinstance(user_id, str) or not user_id.strip():
            return self._failure("User ID must be a non-empty string")

        try:
            requirements = build_constraints(prompt)

            if not isinstance(requirements, dict):
                return self._failure(
                    "Constraint builder returned an invalid result"
                )

            layout = generate_layout(requirements)

            if not isinstance(layout, dict):
                return self._failure(
                    "Planner returned an invalid layout"
                )

            optimized_layout = optimize(layout)

            if not isinstance(optimized_layout, dict):
                return self._failure(
                    "Optimizer returned an invalid layout"
                )

            validation = validate(optimized_layout)

            if not isinstance(validation, dict):
                return self._failure(
                    "Validator returned an invalid result"
                )

            if not validation.get("valid", False):
                return self._failure(
                    "Layout validation failed",
                    validation,
                )

            rooms = optimized_layout.get("rooms", [])
            walls = optimized_layout.get("walls", [])

            if not isinstance(rooms, list) or not rooms:
                return self._failure(
                    "Layout contains no renderable rooms"
                )

            if not isinstance(walls, list):
                return self._failure(
                    "Layout walls must be a list"
                )

            for room in rooms:
                if not isinstance(room, dict):
                    return self._failure(
                        "Layout contains an invalid room object"
                    )

                if not self._valid_polygon(room.get("polygon")):
                    return self._failure(
                        "Layout contains a room with an invalid polygon",
                        {"room": room.get("name", "Unnamed room")},
                    )

            room_result = self._render_rooms(rooms)

            if room_result["skipped"]:
                return self._failure(
                    "One or more room geometries could not be rendered",
                    room_result,
                )

            door_result = self._render_openings(
                optimized_layout.get("doors", []),
                self.door_gen,
                900,
            )

            window_result = self._render_openings(
                optimized_layout.get("windows", []),
                self.window_gen,
                1200,
            )

            stair_result = self._render_stairs(
                optimized_layout.get("stairs", [])
            )

            if stair_result["skipped"]:
                return self._failure(
                    "One or more staircases could not be rendered",
                    stair_result,
                )

            roof = optimized_layout.get("roof")

            if roof is not None:
                self.roof_gen.create_flat_roof(roof)

            slab = optimized_layout.get("slab")

            if slab is not None:
                if not self._valid_polygon(slab):
                    return self._failure(
                        "Layout contains an invalid slab polygon"
                    )

                self.slab_gen.create_slab_from_polygon(slab)

            for room in rooms:
                polygon = room["polygon"]
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

                self.hatch_gen.floor_hatch(polygon)

            plot = optimized_layout.get("plot", {})
            north_x = 1000
            north_y = 1000

            if isinstance(plot, dict):
                north_x = plot.get("width", 1000) + 1000
                north_y = plot.get("height", 1000) + 1000

            self.symbols.north_arrow(north_x, north_y)

            for index, wall in enumerate(walls):
                if not isinstance(wall, dict):
                    continue

                start = wall.get("start")
                end = wall.get("end")

                if not self._valid_point(start) or not self._valid_point(end):
                    continue

                self.dim_gen.linear_dimension(start, end)

            output = self.exporter.export_all(
                base_name=f"floorplan_{user_id}",
                metadata={
                    "prompt": prompt,
                    "requirements": requirements,
                    "validation": validation,
                    "rooms": len(rooms),
                    "rendering": {
                        "doors": door_result,
                        "windows": window_result,
                        "stairs": stair_result,
                        "room_geometry": room_result,
                    },
                },
            )

            return {
                "status": "success",
                "layout": optimized_layout,
                "validation": validation,
                "rendering": {
                    "doors": door_result,
                    "windows": window_result,
                    "stairs": stair_result,
                    "room_geometry": room_result,
                },
                "files": output,
            }

        except Exception as exc:
            return self._failure(
                "Floor-plan rendering failed",
                {
                    "error_type": type(exc).__name__,
                    "message": str(exc),
                },
            )
