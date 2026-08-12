from dataclasses import dataclass

from .geometry.point import Point


@dataclass
class Wall:
    start: Point
    end: Point
    thickness: float = 200
    layer: str = "WALLS"


class WallGenerator:

    def __init__(self, msp):
        self.msp = msp


    def generate_from_edge(self, wall: dict, layer="WALLS"):

        start = wall["start"]
        end = wall["end"]

        self._draw_line(start, end, layer)



    def generate_from_polygon(self, polygon, layer="WALLS"):

        # support SimpleNamespace
        if hasattr(polygon, "vertices"):
            vertices = polygon.vertices
        else:
            vertices = polygon


        if len(vertices) < 3:
            return


        for i in range(len(vertices)):

            start = vertices[i]

            end = vertices[
                (i + 1) % len(vertices)
            ]

            self._draw_line(
                start,
                end,
                layer
            )



    def _draw_line(self, start, end, layer):

        self.msp.add_line(
            self._xy(start),
            self._xy(end),
            dxfattribs={
                "layer": layer
            }
        )


    def _xy(self, p):

        if hasattr(p, "x"):
            return (
                p.x,
                p.y
            )

        return (
            p[0],
            p[1]
        )