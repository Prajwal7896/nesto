from __future__ import annotations

from dataclasses import dataclass
from math import pi, sin, cos, radians, degrees, atan2, acos
from .point import Point
from .bounding_box import BoundingBox


@dataclass(frozen=True)
class Circle:
    """
    Circle Geometry
    """

    center: Point
    radius: float

    @property
    def diameter(self) -> float:
        return self.radius * 2

    @property
    def circumference(self) -> float:
        return 2 * pi * self.radius

    @property
    def area(self) -> float:
        return pi * self.radius ** 2

    @property
    def bounding_box(self) -> BoundingBox:
        return BoundingBox(
            self.center.x - self.radius,
            self.center.y - self.radius,
            self.center.x + self.radius,
            self.center.y + self.radius,
        )

    def contains_point(
        self,
        point: Point
    ) -> bool:

        return (
            self.center.distance_to(point)
            <= self.radius
        )

    def distance_to_point(
        self,
        point: Point
    ) -> float:

        return (
            self.center.distance_to(point)
            - self.radius
        )

    def point_at_angle(
        self,
        angle: float
    ) -> Point:

        angle = radians(angle)

        return Point(
            self.center.x + self.radius * cos(angle),
            self.center.y + self.radius * sin(angle),
        )

    def translate(
        self,
        dx: float,
        dy: float
    ):

        return Circle(
            self.center.translate(dx, dy),
            self.radius,
        )

    def scale(
        self,
        factor: float
    ):

        return Circle(
            self.center.scale(factor),
            self.radius * factor,
        )

    def intersects(
        self,
        other: "Circle"
    ) -> bool:

        d = self.center.distance_to(other.center)

        return (
            d <= self.radius + other.radius
        )

    def tangent_points_from(
        self,
        point: Point
    ):

        d = self.center.distance_to(point)

        if d <= self.radius:
            return []

        theta = atan2(
            point.y - self.center.y,
            point.x - self.center.x,
        )

        alpha = acos(
            self.radius / d
        )

        p1 = self.point_at_angle(
            degrees(theta + alpha)
        )

        p2 = self.point_at_angle(
            degrees(theta - alpha)
        )

        return [p1, p2]

    def to_dict(self):

        return {
            "center": self.center.to_dict(),
            "radius": self.radius,
        }

    @staticmethod
    def from_dict(data):

        return Circle(
            Point.from_dict(data["center"]),
            data["radius"],
        )

    def __repr__(self):

        return (
            f"Circle("
            f"center={self.center}, "
            f"radius={self.radius:.2f})"
        )