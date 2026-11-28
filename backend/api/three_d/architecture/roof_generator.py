
from __future__ import annotations

from typing import Any


class RoofGenerator:
    """Generates roof geometry specifications from a footprint polygon."""

    def __init__(
        self,
        thickness: float = 150.0,
        default_type: str = "flat",
        slope_degrees: float = 0.0,
    ):
        if thickness <= 0:
            raise ValueError("Roof thickness must be positive")

        if not 0 <= slope_degrees < 90:
            raise ValueError("Roof slope must be between 0 and 90 degrees")

        self.thickness = float(thickness)
        self.default_type = default_type
        self.slope_degrees = float(slope_degrees)

    def generate(
        self,
        polygon: list[list[float]],
        elevation: float,
        roof_type: str | None = None,
        slope_degrees: float | None = None,
        material: str = "concrete",
    ) -> dict[str, Any]:
        if not isinstance(polygon, list) or len(polygon) < 3:
            raise ValueError("Roof requires a polygon with at least 3 points")

        roof_type = roof_type or self.default_type
        slope = (
            self.slope_degrees
            if slope_degrees is None
            else float(slope_degrees)
        )

        if not 0 <= slope < 90:
            raise ValueError("Roof slope must be between 0 and 90 degrees")

        if roof_type not in {"flat", "gable", "hip", "shed"}:
            raise ValueError(
                "Supported roof types: flat, gable, hip, shed"
            )

        points = []
        for point in polygon:
            if len(point) != 2:
                raise ValueError("Roof polygon points must be [x, y]")
            points.append([float(point[0]), float(point[1])])

        return {
            "id": "roof",
            "type": "roof",
            "roof_type": roof_type,
            "polygon": points,
            "elevation": float(elevation),
            "thickness": self.thickness,
            "slope_degrees": slope,
            "material": material,
            "unit": "mm",
        }
