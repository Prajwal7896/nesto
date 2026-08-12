from dataclasses import dataclass
from math import sqrt

from .geometry.point import Point
from .geometry.line import Line


@dataclass
class Dimension:
    start: Point
    end: Point
    text: str
    value: float
    layer: str = "DIMENSIONS"


class DimensionGenerator:

    def __init__(self, msp):
        self.msp = msp

    def linear_dimension(
        self,
        start: Point,
        end: Point,
        offset: float = 200,
        layer: str = "DIMENSIONS"
    ):
        """
        Creates a linear dimension between two points.
        """

        value = self._distance(start, end)

        mid = self._midpoint(start, end)

        text = f"{value:.2f} mm"

        dim = Dimension(
            start=start,
            end=end,
            text=text,
            value=value,
            layer=layer
        )

        self._draw_extension_lines(start, end, layer)
        self._draw_dimension_line(start, end, offset, layer)
        self._draw_text(mid, text, layer)

        return dim

    def horizontal_dimension(
        self,
        start: Point,
        end: Point,
        offset: float = 200,
        layer: str = "DIMENSIONS"
    ):
        """
        Horizontal measurement only.
        """

        value = abs(end.x - start.x)

        mid = self._midpoint(start, end)

        text = f"{value:.2f} mm"

        self._draw_dimension_line(start, end, offset, layer)
        self._draw_text(mid, text, layer)

        return Dimension(start, end, text, value, layer)

    def vertical_dimension(
        self,
        start: Point,
        end: Point,
        offset: float = 200,
        layer: str = "DIMENSIONS"
    ):
        """
        Vertical measurement only.
        """

        value = abs(end.y - start.y)

        mid = self._midpoint(start, end)

        text = f"{value:.2f} mm"

        self._draw_dimension_line(start, end, offset, layer)
        self._draw_text(mid, text, layer)

        return Dimension(start, end, text, value, layer)

    def _draw_dimension_line(
        self,
        start: Point,
        end: Point,
        offset: float,
        layer: str
    ):

        self.msp.add_line(
            (start.x, start.y + offset),
            (end.x, end.y + offset),
            dxfattribs={"layer": layer},
        )

    def _draw_extension_lines(
        self,
        start: Point,
        end: Point,
        layer: str
    ):

        self.msp.add_line(
            (start.x, start.y),
            (start.x, start.y + 200),
            dxfattribs={"layer": layer},
        )

        self.msp.add_line(
            (end.x, end.y),
            (end.x, end.y + 200),
            dxfattribs={"layer": layer},
        )

    def _draw_text(
        self,
        position: Point,
        text: str,
        layer: str
    ):

        self.msp.add_text(
            text,
            dxfattribs={
                "layer": layer,
                "height": 120
            }
        ).set_placement(
            (position.x, position.y + 250)
        )

    def _distance(self, a: Point, b: Point):

        return sqrt(
            (a.x - b.x) ** 2 +
            (a.y - b.y) ** 2
        )

    def _midpoint(self, a: Point, b: Point):

        return Point(
            (a.x + b.x) / 2,
            (a.y + b.y) / 2
        )