from dataclasses import dataclass
from math import sqrt

from .geometry.point import Point
from .geometry.line import Line


@dataclass
class Roof:
    boundary: list
    roof_type: str = "flat"
    height: float = 0
    overhang: float = 0
    layer: str = "ROOF"


class RoofGenerator:

    def __init__(self, msp):
        self.msp = msp

    def create_flat_roof(
        self,
        polygon,
        layer="ROOF"
    ):
        """
        Flat roof = same footprint as walls
        """

        roof = Roof(
            boundary=polygon.vertices,
            roof_type="flat",
            layer=layer
        )

        self._draw_outline(polygon.vertices, layer)

        return roof

    def create_gable_roof(
        self,
        polygon,
        ridge_ratio=0.5,
        height=1200,
        layer="ROOF"
    ):
        """
        Simple gable roof (two slopes + ridge line)
        """

        pts = polygon.vertices

        if len(pts) < 4:
            raise ValueError("Gable roof needs rectangular base")

        p1 = pts[0]
        p2 = pts[1]
        p3 = pts[2]
        p4 = pts[3]

        mid1 = self._midpoint(p1, p2)
        mid2 = self._midpoint(p3, p4)

        roof = Roof(
            boundary=pts,
            roof_type="gable",
            height=height,
            layer=layer
        )

        self._draw_outline(pts, layer)
        self._draw_ridge(mid1, mid2, layer)

        self._draw_slope(p1, mid1, layer)
        self._draw_slope(p2, mid1, layer)
        self._draw_slope(p3, mid2, layer)
        self._draw_slope(p4, mid2, layer)

        return roof

    def create_hip_roof(
        self,
        polygon,
        layer="ROOF"
    ):
        """
        Basic hip roof (all sides slope inward)
        """

        pts = polygon.vertices

        center = self._centroid(pts)

        roof = Roof(
            boundary=pts,
            roof_type="hip",
            layer=layer
        )

        self._draw_outline(pts, layer)

        for p in pts:
            self._draw_slope(p, center, layer)

        return roof

    def _draw_outline(self, points, layer):

        n = len(points)

        for i in range(n):

            a = points[i]
            b = points[(i + 1) % n]

            self.msp.add_line(
                (a.x, a.y),
                (b.x, b.y),
                dxfattribs={"layer": layer},
            )

    def _draw_ridge(self, p1, p2, layer):

        self.msp.add_line(
            (p1.x, p1.y),
            (p2.x, p2.y),
            dxfattribs={"layer": layer},
        )

    def _draw_slope(self, p1, p2, layer):

        self.msp.add_line(
            (p1.x, p1.y),
            (p2.x, p2.y),
            dxfattribs={"layer": layer},
        )

    def _midpoint(self, a, b):

        return Point(
            (a.x + b.x) / 2,
            (a.y + b.y) / 2
        )

    def _centroid(self, points):

        x = sum(p.x for p in points) / len(points)
        y = sum(p.y for p in points) / len(points)

        return Point(x, y)