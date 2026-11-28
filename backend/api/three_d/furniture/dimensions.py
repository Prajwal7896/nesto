from __future__ import annotations

from typing import Any

from .library import FurnitureLibrary


class FurnitureDimensions:
    """Resolves and validates furniture dimensions."""

    @staticmethod
    def get_dimensions(
        furniture_type: str,
        overrides: dict[str, Any] | None = None,
    ) -> dict[str, float]:
        definition = FurnitureLibrary.get(furniture_type)
        overrides = overrides or {}

        dimensions = {
            "width": float(overrides.get("width", definition["width"])),
            "depth": float(overrides.get("depth", definition["depth"])),
            "height": float(overrides.get("height", definition["height"])),
        }

        if any(value <= 0 for value in dimensions.values()):
            raise ValueError("Furniture dimensions must be positive")

        return dimensions

    @staticmethod
    def rotated_footprint(
        width: float,
        depth: float,
        rotation: float,
    ) -> tuple[float, float]:
        import math

        angle = math.radians(float(rotation))
        rotated_width = (
            abs(width * math.cos(angle))
            + abs(depth * math.sin(angle))
        )
        rotated_depth = (
            abs(width * math.sin(angle))
            + abs(depth * math.cos(angle))
        )

        return rotated_width, rotated_depth
