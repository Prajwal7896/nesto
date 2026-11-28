
from __future__ import annotations

from typing import Any


class BalconyGenerator:
    """Generates balcony floor and boundary specifications."""

    def __init__(
        self,
        slab_thickness: float = 150.0,
        default_depth: float = 1200.0,
    ):
        if slab_thickness <= 0 or default_depth <= 0:
            raise ValueError("Balcony dimensions must be positive")

        self.slab_thickness = float(slab_thickness)
        self.default_depth = float(default_depth)

    def generate(
        self,
        feature: dict[str, Any],
        elevation: float = 0.0,
    ) -> dict[str, Any]:
        width = float(feature.get("width", 0.0))
        depth = float(feature.get("depth", self.default_depth))

        if width <= 0 or depth <= 0:
            raise ValueError("Balcony width and depth must be positive")

        x = float(feature.get("x", 0.0))
        y = float(feature.get("y", 0.0))

        polygon = feature.get("polygon")
        if not polygon:
            polygon = [
                [x, y],
                [x + width, y],
                [x + width, y + depth],
                [x, y + depth],
            ]

        if len(polygon) < 3:
            raise ValueError("Balcony polygon is invalid")

        return {
            "id": str(feature.get("id", "balcony")),
            "type": "balcony",
            "polygon": [
                [float(point[0]), float(point[1])]
                for point in polygon
            ],
            "elevation": float(elevation),
            "slab_thickness": self.slab_thickness,
            "width": width,
            "depth": depth,
            "railing_required": bool(
                feature.get("railing_required", True)
            ),
            "material": feature.get("material", "concrete"),
            "unit": "mm",
        }
