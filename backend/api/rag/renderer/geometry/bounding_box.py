from __future__ import annotations

from dataclasses import dataclass

from .point import Point


@dataclass(frozen=True)
class BoundingBox:
    """
    Axis-Aligned Bounding Box (AABB)

    Used for:
    - Collision Detection
    - Spatial Search
    - Layout Validation
    - Rendering Optimization
    """

    min_x: float
    min_y: float
    max_x: float
    max_y: float

    @property
    def width(self) -> float:
        return self.max_x - self.min_x

    @property
    def height(self) -> float:
        return self.max_y - self.min_y

    @property
    def area(self) -> float:
        return self.width * self.height

    @property
    def perimeter(self) -> float:
        return 2 * (self.width + self.height)

    @property
    def center(self) -> Point:
        return Point(
            (self.min_x + self.max_x) / 2,
            (self.min_y + self.max_y) / 2
        )

    @property
    def bottom_left(self) -> Point:
        return Point(self.min_x, self.min_y)

    @property
    def bottom_right(self) -> Point:
        return Point(self.max_x, self.min_y)

    @property
    def top_left(self) -> Point:
        return Point(self.min_x, self.max_y)

    @property
    def top_right(self) -> Point:
        return Point(self.max_x, self.max_y)

    @property
    def corners(self):
        return [
            self.bottom_left,
            self.bottom_right,
            self.top_right,
            self.top_left,
        ]

    def contains_point(self, point: Point) -> bool:
        return (
            self.min_x <= point.x <= self.max_x
            and
            self.min_y <= point.y <= self.max_y
        )

    def contains_box(self, other: "BoundingBox") -> bool:
        return (
            self.min_x <= other.min_x
            and
            self.min_y <= other.min_y
            and
            self.max_x >= other.max_x
            and
            self.max_y >= other.max_y
        )

    def intersects(self, other: "BoundingBox") -> bool:
        return not (
            self.max_x < other.min_x
            or self.min_x > other.max_x
            or self.max_y < other.min_y
            or self.min_y > other.max_y
        )

    def intersection(self, other: "BoundingBox"):
        if not self.intersects(other):
            return None

        return BoundingBox(
            max(self.min_x, other.min_x),
            max(self.min_y, other.min_y),
            min(self.max_x, other.max_x),
            min(self.max_y, other.max_y),
        )

    def union(self, other: "BoundingBox"):
        return BoundingBox(
            min(self.min_x, other.min_x),
            min(self.min_y, other.min_y),
            max(self.max_x, other.max_x),
            max(self.max_y, other.max_y),
        )

    def expand(self, value: float):
        return BoundingBox(
            self.min_x - value,
            self.min_y - value,
            self.max_x + value,
            self.max_y + value,
        )

    def shrink(self, value: float):
        return BoundingBox(
            self.min_x + value,
            self.min_y + value,
            self.max_x - value,
            self.max_y - value,
        )

    def translate(self, dx: float, dy: float):
        return BoundingBox(
            self.min_x + dx,
            self.min_y + dy,
            self.max_x + dx,
            self.max_y + dy,
        )

    def scale(self, factor: float):
        cx = self.center.x
        cy = self.center.y

        hw = self.width * factor / 2
        hh = self.height * factor / 2

        return BoundingBox(
            cx - hw,
            cy - hh,
            cx + hw,
            cy + hh,
        )

    def to_dict(self):
        return {
            "min_x": self.min_x,
            "min_y": self.min_y,
            "max_x": self.max_x,
            "max_y": self.max_y,
        }

    @staticmethod
    def from_points(points):
        xs = [p.x for p in points]
        ys = [p.y for p in points]

        return BoundingBox(
            min(xs),
            min(ys),
            max(xs),
            max(ys),
        )

    @staticmethod
    def from_dict(data):
        return BoundingBox(
            data["min_x"],
            data["min_y"],
            data["max_x"],
            data["max_y"],
        )

    def __repr__(self):
        return (
            f"BoundingBox("
            f"min=({self.min_x:.2f}, {self.min_y:.2f}), "
            f"max=({self.max_x:.2f}, {self.max_y:.2f}))"
        )