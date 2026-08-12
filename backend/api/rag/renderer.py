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

        # Generators
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

    def render(self, prompt: str, user_id: str):

        # 1. Build constraints from prompt
        requirements = build_constraints(prompt)

        # 2. Generate layout
        layout = generate_layout(requirements)

        # 3. Optimize layout
        optimized_layout = optimize(layout)

        # 4. Validate layout
        validation = validate(optimized_layout)

        if not validation["valid"]:
            return {
                "status": "failed",
                "reason": validation
            }

        # 5. Extract geometry
        rooms = optimized_layout["rooms"]
        walls = optimized_layout["walls"]

        # 6. WALLS
        for room in rooms:
            polygon = room["polygon"]
            self.wall_gen.generate_from_polygon(polygon)

        # 7. DOORS
        for door in optimized_layout.get("doors", []):
            self.door_gen.place_door_on_wall(
                door["wall"],
                door.get("position", 0.5),
                door.get("width", 900)
            )

        # 8. WINDOWS
        for window in optimized_layout.get("windows", []):
            self.window_gen.place_window_on_wall(
                window["wall"],
                window.get("position", 0.5),
                window.get("width", 1200)
            )

        # 9. STAIRS
        for stair in optimized_layout.get("stairs", []):
            self.stair_gen.create_straight_stair(
                stair["start"],
                stair["end"],
                stair.get("steps", 10)
            )

        # 10. ROOF
        if "roof" in optimized_layout:
            self.roof_gen.create_flat_roof(
                optimized_layout["roof"]
            )

        # 11. SLAB
        if "slab" in optimized_layout:
            self.slab_gen.create_slab_from_polygon(
                optimized_layout["slab"]
            )

        # 12. FURNITURE
        for room in rooms:
            self.furniture_gen.place_furniture(
                room["polygon"],
                room.get("type", "living")
            )

        # 13. LABELS
        for room in rooms:
            self.label_gen.add_room_label(
                room["polygon"],
                room["name"]
            )

            self.label_gen.add_area_label(
                room["polygon"],
                room.get("area", 0)
            )

        # 14. NORTH ARROW
        self.symbols.north_arrow(1000, 1000)

        # 15. HATCH
        for room in rooms:
            self.hatch_gen.floor_hatch(room["polygon"])

        # 16. DIMENSIONS
        for wall in walls:
            self.dim_gen.linear_dimension(
                wall["start"],
                wall["end"]
            )

        # 17. EXPORT
        output = self.exporter.export_all(
            base_name=f"floorplan_{user_id}",
            metadata={
                "prompt": prompt,
                "requirements": requirements,
                "validation": validation,
                "rooms": len(rooms)
            }
        )

        return {
            "status": "success",
            "layout": optimized_layout,
            "validation": validation,
            "files": output
        }