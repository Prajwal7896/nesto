from __future__ import annotations

from dataclasses import dataclass, field
from math import sqrt

from .point import Point
from .bounding_box import BoundingBox


@dataclass
class Spline:
    """
    Polyline-based spline.

    control_points : list of Point
    degree : spline degree (default 3)
    closed : closed spline
    """

    control_points: list[Point] = field(default_factory=list)
    degree: int = 3
    closed: bool = False

    def __post_init__(self):

        if len(self.control_points) < 2:
            raise ValueError(
                "Spline requires at least two control points."
            )

    @property
    def count(self):

        return len(self.control_points)

    @property
    def bounding_box(self):

        xs = [p.x for p in self.control_points]
        ys = [p.y for p in self.control_points]

        return BoundingBox(
            min(xs),
            min(ys),
            max(xs),
            max(ys)
        )

    @property
    def length(self):

        total = 0.0

        for i in range(len(self.control_points) - 1):

            total += self.control_points[i].distance_to(
                self.control_points[i + 1]
            )

        if self.closed:

            total += self.control_points[-1].distance_to(
                self.control_points[0]
            )

        return total

    def add_point(
        self,
        point: Point
    ):

        self.control_points.append(point)

    def point_at(
        self,
        t: float
    ):

        """
        Linear interpolation.
        t ∈ [0,1]
        """

        if t <= 0:
            return self.control_points[0]

        if t >= 1:
            return self.control_points[-1]

        total = self.length

        target = total * t

        travelled = 0

        for i in range(len(self.control_points) - 1):

            a = self.control_points[i]
            b = self.control_points[i + 1]

            d = a.distance_to(b)

            if travelled + d >= target:

                local = (
                    target - travelled
                ) / d

                return a.lerp(b, local)

            travelled += d

        return self.control_points[-1]

    def translate(
        self,
        dx,
        dy
    ):

        return Spline(
            [
                p.translate(dx, dy)
                for p in self.control_points
            ],
            self.degree,
            self.closed
        )

    def scale(
        self,
        factor
    ):

        return Spline(
            [
                p.scale(factor)
                for p in self.control_points
            ],
            self.degree,
            self.closed
        )

    def rotate(
        self,
        angle,
        origin=None
    ):

        return Spline(
            [
                p.rotate(angle, origin)
                for p in self.control_points
            ],
            self.degree,
            self.closed
        )

    def reverse(self):

        return Spline(
            list(
                reversed(
                    self.control_points
                )
            ),
            self.degree,
            self.closed
        )

    def to_dict(self):

        return {

            "degree": self.degree,

            "closed": self.closed,

            "control_points": [

                p.to_dict()

                for p in self.control_points

            ]

        }

    @staticmethod
    def from_dict(data):

        return Spline(

            [

                Point.from_dict(p)

                for p in data["control_points"]

            ],

            data.get("degree", 3),

            data.get("closed", False)

        )

    def __len__(self):

        return len(self.control_points)

    def __iter__(self):

        return iter(self.control_points)

    def __getitem__(self, item):

        return self.control_points[item]

    def __repr__(self):

        return (
            f"Spline("
            f"{len(self.control_points)} control points, "
            f"degree={self.degree}, "
            f"closed={self.closed})"
        )