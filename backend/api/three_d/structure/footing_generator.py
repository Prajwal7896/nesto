from __future__ import annotations

from typing import Any


class FootingGenerator:
    """Creates isolated footing geometry specifications."""

    def __init__(
        self,
        default_width: float = 1500.0,
        default_depth: float = 1500.0,
        default_thickness: float = 450.0,
    ):
        if min(default_width, default_depth, default_thickness) <= 0:
            raise ValueError("Footing dimensions must be positive")

        self.default_width = float(default_width)
        self.default_depth = float(default_depth)
        self.default_thickness = float(default_thickness)

    def generate(
        self,
        column_positions: list[dict[str, Any]],
        elevation: float = -1200.0,
    ) -> list[dict[str, Any]]:
        if not isinstance(column_positions, list):
            raise TypeError("column_positions must be a list")

        footings = []

        for index, column in enumerate(column_positions):
            x = float(column["x"])
            y = float(column["y"])
            width = float(column.get("footing_width", self.default_width))
            depth = float(column.get("footing_depth", self.default_depth))
            thickness = float(
                column.get("footing_thickness", self.default_thickness)
            )

            if min(width, depth, thickness) <= 0:
                raise ValueError("Footing dimensions must be positive")

            footings.append({
                "id": f"footing_{index + 1}",
                "type": "isolated_footing",
                "column_id": column.get("id"),
                "center": [x, y],
                "width": width,
                "depth": depth,
                "thickness": thickness,
                "elevation": float(elevation),
                "material": "reinforced_concrete",
                "unit": "mm",
            })

        return footings
