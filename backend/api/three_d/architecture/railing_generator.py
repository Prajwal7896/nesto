
from __future__ import annotations

from typing import Any
import math


class RailingGenerator:
    """Generates railing posts and horizontal rails along a polygon."""

    def __init__(
        self,
        height: float = 1050.0,
        post_spacing: float = 1000.0,
        post_width: float = 40.0,
        rail_count: int = 2,
    ):
        if min(height, post_spacing, post_width) <= 0:
            raise ValueError("Railing dimensions must be positive")

        if rail_count < 1:
            raise ValueError("rail_count must be at least 1")

        self.height = float(height)
        self.post_spacing = float(post_spacing)
        self.post_width = float(post_width)
        self.rail_count = int(rail_count)

    def generate(
        self,
        polygon: list[list[float]],
        base_elevation: float = 0.0,
        material: str = "metal",
    ) -> dict[str, Any]:
        if not isinstance(polygon, list) or len(polygon) < 3:
            raise ValueError("Railing requires a valid polygon")

        posts = []
        rails = []

        for edge_index, start in enumerate(polygon):
            end = polygon[(edge_index + 1) % len(polygon)]

            x1, y1 = float(start[0]), float(start[1])
            x2, y2 = float(end[0]), float(end[1])

            length = math.hypot(x2 - x1, y2 - y1)
            if length <= 0:
                continue

            divisions = max(1, math.ceil(length / self.post_spacing))

            for step in range(divisions + 1):
                t = step / divisions
                posts.append({
                    "id": f"post_{edge_index}_{step}",
                    "position": [
                        x1 + (x2 - x1) * t,
                        y1 + (y2 - y1) * t,
                    ],
                    "base_elevation": float(base_elevation),
                    "height": self.height,
                    "width": self.post_width,
                })

            for rail_index in range(self.rail_count):
                rail_height = self.height * (
                    (rail_index + 1) / (self.rail_count + 1)
                )

                rails.append({
                    "id": f"rail_{edge_index}_{rail_index}",
                    "start": [x1, y1],
                    "end": [x2, y2],
                    "elevation": float(base_elevation) + rail_height,
                    "thickness": self.post_width,
                })

        return {
            "id": "railing",
            "type": "railing",
            "height": self.height,
            "posts": posts,
            "rails": rails,
            "material": material,
            "unit": "mm",
        }
