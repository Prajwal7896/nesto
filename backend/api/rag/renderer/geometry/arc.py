from __future__ import annotations

from dataclasses import dataclass
from math import radians, degrees, sin, cos, pi

from .point import Point


@dataclass
class Arc:
    """
    Circular Arc

    center : Point
    radius : millimeters
    start_angle : degrees
    end_angle : degrees
    """

    center: Point
    radius: float
    start_angle: float
    end_angle: float

    @property
    def sweep_angle(self) -> float:
        angle = self.end_angle - self.start_angle
        if angle < 0:
            angle += 360
        return angle

    @property
    def length(self) -> float:
        return (
            2 * pi * self.radius
        ) * (self.sweep_angle / 360)

    @property
    def diameter(self) -> float:
        return self.radius * 2

    @property
    def circumference(self) -> float:
        return 2 * pi * self.radius

    @property
    def area(self) -> float:
        return (
            pi * self.radius ** 2
        ) * (self.sweep_angle / 360)

    @property
    def start_point(self) -> Point:

        angle = radians(self.start_angle)

        return Point(
            self.center.x + self.radius * cos(angle),
            self.center.y + self.radius * sin(angle)
        )

    @property
    def end_point(self) -> Point:

        angle = radians(self.end_angle)

        return Point(
            self.center.x + self.radius * cos(angle),
            self.center.y + self.radius * sin(angle)
        )

    @property
    def midpoint(self) -> Point:

        angle = radians(
            self.start_angle + self.sweep_angle / 2
        )

        return Point(
            self.center.x + self.radius * cos(angle),
            self.center.y + self.radius * sin(angle)
        )

    def point_at(self, t: float) -> Point:
        """
        t in [0,1]
        """

        angle = radians(
            self.start_angle +
            self.sweep_angle * t
        )

        return Point(
            self.center.x + self.radius * cos(angle),
            self.center.y + self.radius * sin(angle)
        )

    def contains_angle(
        self,
        angle: float
    ) -> bool:

        angle %= 360

        start = self.start_angle % 360
        end = self.end_angle % 360

        if start <= end:
            return start <= angle <= end

        return angle >= start or angle <= end

    def translate(
        self,
        dx: float,
        dy: float
    ):

        return Arc(
            self.center.translate(dx, dy),
            self.radius,
            self.start_angle,
            self.end_angle
        )

    def scale(
        self,
        factor: float
    ):

        return Arc(
            self.center.scale(factor),
            self.radius * factor,
            self.start_angle,
            self.end_angle
        )

    def rotate(
        self,
        angle: float
    ):

        return Arc(
            self.center,
            self.radius,
            self.start_angle + angle,
            self.end_angle + angle
        )

    def reverse(self):

        return Arc(
            self.center,
            self.radius,
            self.end_angle,
            self.start_angle
        )

    def to_dict(self):

        return {
            "center": self.center.to_dict(),
            "radius": self.radius,
            "start_angle": self.start_angle,
            "end_angle": self.end_angle
        }

    @staticmethod
    def from_dict(data):

        return Arc(
            Point.from_dict(data["center"]),
            data["radius"],
            data["start_angle"],
            data["end_angle"]
        )

    def __repr__(self):

        return (
            f"Arc("
            f"center={self.center}, "
            f"radius={self.radius:.2f}, "
            f"start={self.start_angle:.2f}, "
            f"end={self.end_angle:.2f})"
        )