from __future__ import annotations

from dataclasses import dataclass
from math import sqrt, radians, sin, cos


@dataclass(frozen=True)
class Point:
    """
    2D Point
    Units: millimeters
    """

    x: float
    y: float

    @property
    def tuple(self):
        return (self.x, self.y)

    def distance_to(
        self,
        other: "Point"
    ) -> float:

        return sqrt(
            (self.x - other.x) ** 2 +
            (self.y - other.y) ** 2
        )

    def midpoint(
        self,
        other: "Point"
    ):

        return Point(
            (self.x + other.x) / 2,
            (self.y + other.y) / 2
        )

    def translate(
        self,
        dx: float,
        dy: float
    ):

        return Point(
            self.x + dx,
            self.y + dy
        )

    def scale(
        self,
        factor: float
    ):

        return Point(
            self.x * factor,
            self.y * factor
        )

    def rotate(
        self,
        angle: float,
        origin: "Point" = None
    ):

        if origin is None:
            origin = Point(0, 0)

        angle = radians(angle)

        tx = self.x - origin.x
        ty = self.y - origin.y

        rx = tx * cos(angle) - ty * sin(angle)
        ry = tx * sin(angle) + ty * cos(angle)

        return Point(
            rx + origin.x,
            ry + origin.y
        )

    def mirror_x(self):

        return Point(
            self.x,
            -self.y
        )

    def mirror_y(self):

        return Point(
            -self.x,
            self.y
        )

    def lerp(
        self,
        other: "Point",
        t: float
    ):

        return Point(
            self.x + (other.x - self.x) * t,
            self.y + (other.y - self.y) * t
        )

    def almost_equal(
        self,
        other: "Point",
        tolerance: float = 1e-6
    ):

        return (
            abs(self.x - other.x) <= tolerance
            and
            abs(self.y - other.y) <= tolerance
        )

    def to_dict(self):

        return {
            "x": self.x,
            "y": self.y
        }

    @staticmethod
    def from_dict(data):

        return Point(
            data["x"],
            data["y"]
        )

    def __iter__(self):

        yield self.x
        yield self.y

    def __repr__(self):

        return (
            f"Point("
            f"{self.x:.2f}, "
            f"{self.y:.2f})"
        )