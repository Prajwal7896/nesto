from __future__ import annotations

from dataclasses import dataclass
from math import sqrt, atan2, degrees, radians, sin, cos

from .point import Point


@dataclass(frozen=True)
class Vector:
    """
    2D Vector
    """

    x: float
    y: float

    @property
    def length(self):

        return sqrt(
            self.x ** 2 +
            self.y ** 2
        )

    @property
    def magnitude(self):

        return self.length

    @property
    def angle(self):

        return degrees(
            atan2(
                self.y,
                self.x
            )
        )

    def normalize(self):

        l = self.length

        if l == 0:
            return Vector(0, 0)

        return Vector(
            self.x / l,
            self.y / l
        )

    def perpendicular(self):

        return Vector(
            -self.y,
            self.x
        )

    def reverse(self):

        return Vector(
            -self.x,
            -self.y
        )

    def scale(
        self,
        factor
    ):

        return Vector(
            self.x * factor,
            self.y * factor
        )

    def dot(
        self,
        other
    ):

        return (
            self.x * other.x +
            self.y * other.y
        )

    def cross(
        self,
        other
    ):

        return (
            self.x * other.y -
            self.y * other.x
        )

    def angle_to(
        self,
        other
    ):

        a = self.normalize()
        b = other.normalize()

        dot = max(
            -1.0,
            min(
                1.0,
                a.dot(b)
            )
        )

        from math import acos

        return degrees(
            acos(dot)
        )

    def rotate(
        self,
        angle
    ):

        angle = radians(angle)

        return Vector(

            self.x * cos(angle)
            -
            self.y * sin(angle),

            self.x * sin(angle)
            +
            self.y * cos(angle)

        )

    def to_point(self):

        return Point(
            self.x,
            self.y
        )

    @staticmethod
    def from_points(
        p1: Point,
        p2: Point
    ):

        return Vector(
            p2.x - p1.x,
            p2.y - p1.y
        )

    def to_dict(self):

        return {
            "x": self.x,
            "y": self.y
        }

    @staticmethod
    def from_dict(data):

        return Vector(
            data["x"],
            data["y"]
        )

    def __add__(
        self,
        other
    ):

        return Vector(
            self.x + other.x,
            self.y + other.y
        )

    def __sub__(
        self,
        other
    ):

        return Vector(
            self.x - other.x,
            self.y - other.y
        )

    def __mul__(
        self,
        scalar
    ):

        return Vector(
            self.x * scalar,
            self.y * scalar
        )

    __rmul__ = __mul__

    def __truediv__(
        self,
        scalar
    ):

        return Vector(
            self.x / scalar,
            self.y / scalar
        )

    def __neg__(self):

        return Vector(
            -self.x,
            -self.y
        )

    def __repr__(self):

        return (
            f"Vector("
            f"{self.x:.3f}, "
            f"{self.y:.3f})"
        )