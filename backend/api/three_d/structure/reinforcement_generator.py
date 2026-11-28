from __future__ import annotations

from typing import Any
import math


class ReinforcementGenerator:
    """Creates visual reinforcement bar specifications.

    Visualization only. This does not calculate or certify structural design.
    """

    def __init__(
        self,
        default_bar_diameter: float = 12.0,
        default_spacing: float = 150.0,
        default_cover: float = 40.0,
    ):
        if min(
            default_bar_diameter,
            default_spacing,
            default_cover,
        ) <= 0:
            raise ValueError("Reinforcement parameters must be positive")

        self.default_bar_diameter = float(default_bar_diameter)
        self.default_spacing = float(default_spacing)
        self.default_cover = float(default_cover)

    def generate_slab_mesh(
        self,
        polygon: list[list[float]],
        elevation: float,
        thickness: float,
        spacing: float | None = None,
        diameter: float | None = None,
        cover: float | None = None,
    ) -> dict[str, Any]:
        if not isinstance(polygon, list) or len(polygon) != 4:
            raise ValueError(
                "Requires a rectangular four-point polygon"
            )

        spacing = float(
            self.default_spacing if spacing is None else spacing
        )
        diameter = float(
            self.default_bar_diameter if diameter is None else diameter
        )
        cover = float(
            self.default_cover if cover is None else cover
        )
        thickness = float(thickness)

        if min(spacing, diameter, cover, thickness) <= 0:
            raise ValueError("Reinforcement dimensions must be positive")

        xs = [float(point[0]) for point in polygon]
        ys = [float(point[1]) for point in polygon]

        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)

        inner_min_x = min_x + cover
        inner_max_x = max_x - cover
        inner_min_y = min_y + cover
        inner_max_y = max_y - cover

        if inner_min_x >= inner_max_x or inner_min_y >= inner_max_y:
            raise ValueError("Cover leaves no space for reinforcement")

        x_count = max(
            1, math.floor((inner_max_x - inner_min_x) / spacing) + 1
        )
        y_count = max(
            1, math.floor((inner_max_y - inner_min_y) / spacing) + 1
        )

        bars = []

        for index in range(y_count):
            y = inner_min_y + index * spacing
            bars.append({
                "id": f"bar_x_{index + 1}",
                "start": [inner_min_x, y],
                "end": [inner_max_x, y],
                "elevation": float(elevation) + cover,
                "diameter": diameter,
                "direction": "x",
            })

        for index in range(x_count):
            x = inner_min_x + index * spacing
            bars.append({
                "id": f"bar_y_{index + 1}",
                "start": [x, inner_min_y],
                "end": [x, inner_max_y],
                "elevation": float(elevation) + cover + diameter,
                "diameter": diameter,
                "direction": "y",
            })

        return {
            "type": "slab_reinforcement",
            "bars": bars,
            "bar_count": len(bars),
            "spacing": spacing,
            "diameter": diameter,
            "cover": cover,
            "slab_thickness": thickness,
            "unit": "mm",
            "visualization_only": True,
        }
