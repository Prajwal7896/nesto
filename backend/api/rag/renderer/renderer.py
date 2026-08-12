import ezdxf
from types import SimpleNamespace
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
    from types import SimpleNamespace
    from .geometry.point import Point

    def _normalize_polygon(self, polygon):
        """
        Ensures polygon always has:
        - vertices: List[Point]
        - edges: List[Line]
        """

        if hasattr(polygon, "vertices"):
            vertices = polygon.vertices
        else:
            vertices = polygon

        # convert tuples → Point
        vertices = [
            p if isinstance(p, Point) else Point(p[0], p[1])
            for p in vertices
        ]

        # build edges dynamically
        edges = []
        from .geometry.line import Line

        for i in range(len(vertices)):
            edges.append(Line(vertices[i], vertices[(i + 1) % len(vertices)]))

        return SimpleNamespace(
            vertices=vertices,
            edges=edges
        )
    
    def render(self, layout: dict, prompt: str, user_id: str):

        rooms = layout.get("rooms", [])
        walls = layout.get("walls", [])
        doors = layout.get("doors", [])
        windows = layout.get("windows", [])

        all_walls = []


        print("\n========== ROOMS ==========")

        for room in rooms:

            print(
                room.get("type"),
                room.get("polygon")
            )

            polygon = self._normalize_polygon(
                room.get("polygon", [])
            )


            if len(polygon.vertices) < 3:
                print("Invalid polygon skipped")
                continue


            # ----------------------------
            # WALLS
            # ----------------------------

            for i in range(len(polygon.vertices)):

                start = polygon.vertices[i]

                end = polygon.vertices[
                    (i + 1) % len(polygon.vertices)
                ]


                wall = {
                    "start": start,
                    "end": end
                }


                all_walls.append(wall)


            # FIX
            self.wall_gen.generate_from_polygon(polygon)


        print("==========================\n")



        # ----------------------------
        # DOORS
        # ----------------------------

        for door in doors:

            if door["wall"] < len(all_walls):

                self.door_gen.place_door_on_wall(
                    wall=all_walls[door["wall"]],
                    position_t=door.get(
                        "position",
                        0.5
                    ),
                    width=door.get(
                        "width",
                        900
                    )
                )



        # ----------------------------
        # WINDOWS
        # ----------------------------

        for window in windows:

            if window["wall"] < len(all_walls):

                self.window_gen.place_window_on_wall(
                    wall=all_walls[window["wall"]],
                    position_t=window.get(
                        "position",
                        0.5
                    ),
                    width=window.get(
                        "width",
                        1200
                    )
                )



        # ----------------------------
        # FURNITURE / LABEL / HATCH
        # ----------------------------

        for room in rooms:


            polygon = self._normalize_polygon(
                room.get("polygon", [])
            )


            if len(polygon.vertices) < 3:
                continue


            self.furniture_gen.place_furniture(
                polygon,
                room.get(
                    "type",
                    "living"
                )
            )


            self.label_gen.add_room_label(
                polygon,
                room.get(
                    "name",
                    room.get(
                        "type",
                        "room"
                    )
                )
            )


            self.label_gen.add_area_label(
                polygon,
                room.get(
                    "area",
                    0
                )
            )


            self.hatch_gen.floor_hatch(
                polygon
            )



        return self.exporter.export_all(
            base_name=f"floorplan_{user_id}",
            metadata={
                "prompt": prompt,
                "rooms": len(rooms)
            }
        )
    
    
    def render_2d(self, layout: dict, prompt: str, user_id: str):
        """
        Convenience function used by the pipeline.
        """
        renderer = Renderer()
        return renderer.render(layout, prompt, user_id)