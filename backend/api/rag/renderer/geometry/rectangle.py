from __future__ import annotations

from dataclasses import dataclass

from .point import Point
from .line import Line
from .polygon import Polygon
from .bounding_box import BoundingBox


@dataclass(frozen=True)
class Rectangle:
    """
    Axis-Aligned Rectangle
    Units: millimeters
    """

    x: float
    y: float
    width: float
    height: float

    def __post_init__(self):

        if self.width <= 0:
            raise ValueError("Width must be positive.")

        if self.height <= 0:
            raise ValueError("Height must be positive.")

    @property
    def area(self) -> float:
        return self.width * self.height

    @property
    def perimeter(self) -> float:
        return 2 * (self.width + self.height)

    @property
    def center(self) -> Point:
        return Point(
            self.x + self.width / 2,
            self.y + self.height / 2
        )

    @property
    def bottom_left(self) -> Point:
        return Point(self.x, self.y)

    @property
    def bottom_right(self) -> Point:
        return Point(
            self.x + self.width,
            self.y
        )

    @property
    def top_right(self) -> Point:
        return Point(
            self.x + self.width,
            self.y + self.height
        )

    @property
    def top_left(self) -> Point:
        return Point(
            self.x,
            self.y + self.height
        )

    @property
    def corners(self):

        return [
            self.bottom_left,
            self.bottom_right,
            self.top_right,
            self.top_left
        ]

    @property
    def edges(self):

        c = self.corners

        return [
            Line(c[0], c[1]),
            Line(c[1], c[2]),
            Line(c[2], c[3]),
            Line(c[3], c[0]),
        ]

    @property
    def bounding_box(self):

        return BoundingBox(
            self.x,
            self.y,
            self.x + self.width,
            self.y + self.height
        )

    def contains_point(
        self,
        point: Point
    ) -> bool:

        return (
            self.x <= point.x <= self.x + self.width
            and
            self.y <= point.y <= self.y + self.height
        )

    def intersects(
        self,
        other: "Rectangle"
    ) -> bool:

        return self.bounding_box.intersects(
            other.bounding_box
        )

    def translate(
        self,
        dx: float,
        dy: float
    ):

        return Rectangle(
            self.x + dx,
            self.y + dy,
            self.width,
            self.height
        )

    def scale(
        self,
        factor: float
    ):

        return Rectangle(
            self.x * factor,
            self.y * factor,
            self.width * factor,
            self.height * factor
        )

    def to_polygon(self):

        return Polygon(
            self.corners
        )

    def to_dict(self):

        return {
            "x": self.x,
            "y": self.y,
            "width": self.width,
            "height": self.height
        }

    @staticmethod
    def from_dict(data):

        return Rectangle(
            data["x"],
            data["y"],
            data["width"],
            data["height"]
        )

    def __repr__(self):

        return (
            f"Rectangle("
            f"x={self.x:.2f}, "
            f"y={self.y:.2f}, "
            f"width={self.width:.2f}, "
            f"height={self.height:.2f})"
        )