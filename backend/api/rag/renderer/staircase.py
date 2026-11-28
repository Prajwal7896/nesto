from dataclasses import dataclass
from math import sqrt

from .geometry.point import Point
from .geometry.line import Line


@dataclass
class Staircase:
    start: Point
    end: Point
    steps: int = 10
    width: float = 1000
    layer: str = "STAIRCASE"


class StaircaseGenerator:

    def __init__(self, msp):
        self.msp = msp

    def create_straight_stair(
        self,
        start: Point,
        end: Point,
        steps: int = 10,
        width: float = 1000,
        layer: str = "STAIRCASE"
    ):
        """
        Straight staircase with step divisions.
        """

        stair = Staircase(start, end, steps, width, layer)

        self._draw_stair_outline(start, end, width, layer)
        self._draw_steps(start, end, steps, layer)
        self._draw_direction_arrow(start, end, layer)

        return stair

    def _draw_stair_outline(
        self,
        start: Point,
        end: Point,
        width: float,
        layer: str
    ):

        self.msp.add_line(
            (start.x, start.y),
            (end.x, end.y),
            dxfattribs={"layer": layer},
        )

    def _draw_steps(
        self,
        start: Point,
        end: Point,
        steps: int,
        layer: str
    ):

        dx = (end.x - start.x) / steps
        dy = (end.y - start.y) / steps

        for i in range(steps + 1):

            p = Point(
                start.x + dx * i,
                start.y + dy * i
            )

            self.msp.add_line(
                (p.x - dy * 0.2, p.y + dx * 0.2),
                (p.x + dy * 0.2, p.y - dx * 0.2),
                dxfattribs={"layer": layer},
            )

    def _draw_direction_arrow(
        self,
        start: Point,
        end: Point,
        layer: str
    ):

        mid = Point(
            (start.x + end.x) / 2,
            (start.y + end.y) / 2
        )

        self.msp.add_line(
            (mid.x, mid.y),
            (end.x, end.y),
            dxfattribs={"layer": layer},
        )

        # arrow head
        dx = end.x - mid.x
        dy = end.y - mid.y

        length = sqrt(dx * dx + dy * dy)

        if length == 0:
            return

        ux = dx / length
        uy = dy / length

        size = 200

        left = (
            end.x - ux * size + uy * size * 0.5,
            end.y - uy * size - ux * size * 0.5
        )

        right = (
            end.x - ux * size - uy * size * 0.5,
            end.y - uy * size + ux * size * 0.5
        )

        self.msp.add_line(
            (end.x, end.y),
            left,
            dxfattribs={"layer": layer},
        )

        self.msp.add_line(
            (end.x, end.y),
            right,
            dxfattribs={"layer": layer},
        )

    def create_l_shaped_stair(
        self,
        p1: Point,
        corner: Point,
        p2: Point,
        steps: int = 10,
        layer: str = "STAIRCASE"
    ):
        """
        L-shaped staircase (two segments).
        """

        half_steps = steps // 2

        self.create_straight_stair(
            p1,
            corner,
            half_steps,
            layer=layer
        )

        self.create_straight_stair(
            corner,
            p2,
            half_steps,
            layer=layer
        )

    def create_u_shaped_stair(
        self,
        p1: Point,
        p2: Point,
        offset: float = 2000,
        steps: int = 14,
        layer: str = "STAIRCASE"
    ):
        """
        U-shaped return staircase.
        """

        mid1 = Point(p1.x + offset, p1.y)
        mid2 = Point(p2.x + offset, p2.y)

        half = steps // 2

        self.create_straight_stair(p1, mid1, half, layer=layer)
        self.create_straight_stair(mid2, p2, half, layer=layer)

        self.msp.add_line(
            (mid1.x, mid1.y),
            (mid2.x, mid2.y),
            dxfattribs={"layer": layer},
        )