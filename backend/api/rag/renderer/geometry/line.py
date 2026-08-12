from __future__ import annotations

from dataclasses import dataclass
from math import atan2, degrees

from .point import Point
from .vector import Vector


@dataclass(frozen=True)
class Line:
    """
    2D Line Segment
    """

    start: Point
    end: Point

    @property
    def length(self) -> float:
        return self.start.distance_to(self.end)

    @property
    def direction(self) -> Vector:
        return Vector(
            self.end.x - self.start.x,
            self.end.y - self.start.y
        )

    @property
    def midpoint(self) -> Point:
        return Point(
            (self.start.x + self.end.x) / 2,
            (self.start.y + self.end.y) / 2
        )

    @property
    def angle(self) -> float:
        return degrees(
            atan2(
                self.end.y - self.start.y,
                self.end.x - self.start.x
            )
        )

    @property
    def is_horizontal(self) -> bool:
        return abs(self.start.y - self.end.y) < 1e-9

    @property
    def is_vertical(self) -> bool:
        return abs(self.start.x - self.end.x) < 1e-9

    def reverse(self):
        return Line(self.end, self.start)

    def translate(
        self,
        dx: float,
        dy: float
    ):
        return Line(
            self.start.translate(dx, dy),
            self.end.translate(dx, dy)
        )

    def scale(
        self,
        factor: float
    ):
        return Line(
            self.start.scale(factor),
            self.end.scale(factor)
        )

    def point_at(
        self,
        t: float
    ):
        """
        t in [0,1]
        """

        return Point(
            self.start.x + (self.end.x - self.start.x) * t,
            self.start.y + (self.end.y - self.start.y) * t
        )

    def contains_point(
        self,
        point: Point,
        tolerance: float = 1e-6
    ):

        d1 = self.start.distance_to(point)
        d2 = self.end.distance_to(point)

        return abs(
            d1 + d2 - self.length
        ) <= tolerance

    def closest_point(
        self,
        point: Point
    ):

        dx = self.end.x - self.start.x
        dy = self.end.y - self.start.y

        if dx == 0 and dy == 0:
            return self.start

        t = (
            (
                (point.x - self.start.x) * dx
                +
                (point.y - self.start.y) * dy
            )
            /
            (dx * dx + dy * dy)
        )

        t = max(0.0, min(1.0, t))

        return self.point_at(t)

    def distance_to_point(
        self,
        point: Point
    ):
        return point.distance_to(
            self.closest_point(point)
        )

    def extend(
        self,
        distance: float
    ):

        direction = self.direction.normalize()

        return Line(
            Point(
                self.start.x - direction.x * distance,
                self.start.y - direction.y * distance
            ),
            Point(
                self.end.x + direction.x * distance,
                self.end.y + direction.y * distance
            )
        )

    def offset(
        self,
        distance: float
    ):

        n = self.direction.normalize().perpendicular()

        return Line(
            Point(
                self.start.x + n.x * distance,
                self.start.y + n.y * distance
            ),
            Point(
                self.end.x + n.x * distance,
                self.end.y + n.y * distance
            )
        )

    def to_vector(self):
        return self.direction

    def to_dict(self):

        return {
            "start": self.start.to_dict(),
            "end": self.end.to_dict()
        }

    @staticmethod
    def from_dict(data):

        return Line(
            Point.from_dict(data["start"]),
            Point.from_dict(data["end"])
        )

    def __repr__(self):

        return (
            f"Line("
            f"{self.start} -> "
            f"{self.end})"
        )