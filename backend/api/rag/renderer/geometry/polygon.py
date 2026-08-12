from __future__ import annotations

from dataclasses import dataclass
from math import atan2

from .point import Point
from .line import Line
from .bounding_box import BoundingBox


@dataclass
class Polygon:

    vertices: list[Point]

    def __post_init__(self):

        if len(self.vertices) < 3:
            raise ValueError(
                "Polygon requires at least 3 vertices."
            )

    @property
    def edges(self):

        edges = []

        n = len(self.vertices)

        for i in range(n):

            edges.append(
                Line(
                    self.vertices[i],
                    self.vertices[(i + 1) % n]
                )
            )

        return edges

    @property
    def perimeter(self):

        return sum(
            edge.length
            for edge in self.edges
        )

    @property
    def area(self):

        area = 0

        n = len(self.vertices)

        for i in range(n):

            j = (i + 1) % n

            area += (
                self.vertices[i].x *
                self.vertices[j].y
            )

            area -= (
                self.vertices[j].x *
                self.vertices[i].y
            )

        return abs(area) / 2

    @property
    def centroid(self):

        cx = 0
        cy = 0

        a = 0

        n = len(self.vertices)

        for i in range(n):

            j = (i + 1) % n

            cross = (
                self.vertices[i].x *
                self.vertices[j].y
                -
                self.vertices[j].x *
                self.vertices[i].y
            )

            a += cross

            cx += (
                self.vertices[i].x +
                self.vertices[j].x
            ) * cross

            cy += (
                self.vertices[i].y +
                self.vertices[j].y
            ) * cross

        a *= 0.5

        if abs(a) < 1e-9:
            return Point(0, 0)

        cx /= (6 * a)
        cy /= (6 * a)

        return Point(cx, cy)

    @property
    def bounding_box(self):

        xs = [
            p.x
            for p in self.vertices
        ]

        ys = [
            p.y
            for p in self.vertices
        ]

        return BoundingBox(
            min(xs),
            min(ys),
            max(xs),
            max(ys)
        )

    @property
    def is_clockwise(self):

        s = 0

        n = len(self.vertices)

        for i in range(n):

            j = (i + 1) % n

            s += (
                self.vertices[j].x -
                self.vertices[i].x
            ) * (
                self.vertices[j].y +
                self.vertices[i].y
            )

        return s > 0

    def reverse(self):

        return Polygon(
            list(
                reversed(
                    self.vertices
                )
            )
        )

    def translate(
        self,
        dx,
        dy
    ):

        return Polygon(
            [
                p.translate(dx, dy)
                for p in self.vertices
            ]
        )

    def scale(
        self,
        factor
    ):

        return Polygon(
            [
                p.scale(factor)
                for p in self.vertices
            ]
        )

    def rotate(
        self,
        angle,
        origin=None
    ):

        return Polygon(
            [
                p.rotate(
                    angle,
                    origin
                )
                for p in self.vertices
            ]
        )

    def contains_point(
        self,
        point
    ):

        inside = False

        n = len(self.vertices)

        j = n - 1

        for i in range(n):

            pi = self.vertices[i]
            pj = self.vertices[j]

            if (
                (
                    pi.y > point.y
                )
                !=
                (
                    pj.y > point.y
                )
            ):

                xinters = (
                    (pj.x - pi.x)
                    *
                    (
                        point.y - pi.y
                    )
                    /
                    (
                        pj.y - pi.y
                    )
                    +
                    pi.x
                )

                if point.x < xinters:

                    inside = not inside

            j = i

        return inside

    def to_dict(self):

        return {

            "vertices": [

                p.to_dict()

                for p in self.vertices

            ]

        }

    @staticmethod
    def from_dict(data):

        return Polygon(

            [

                Point.from_dict(p)

                for p in data["vertices"]

            ]

        )

    def __len__(self):

        return len(
            self.vertices
        )

    def __iter__(self):

        return iter(
            self.vertices
        )

    def __getitem__(
        self,
        item
    ):

        return self.vertices[item]

    def __repr__(self):

        return (
            f"Polygon("
            f"{len(self.vertices)} vertices)"
        )