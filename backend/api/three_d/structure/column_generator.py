from __future__ import annotations

from typing import Any


class ColumnGenerator:
    """Creates vertical column geometry specifications."""

    def __init__(
        self,
        default_width: float = 300.0,
        default_depth: float = 300.0,
        default_height: float = 3000.0,
    ):
        if min(default_width, default_depth, default_height) <= 0:
            raise ValueError("Column dimensions must be positive")

        self.default_width = float(default_width)
        self.default_depth = float(default_depth)
        self.default_height = float(default_height)

    def generate(
        self,
        positions: list[dict[str, Any]],
        floor_elevation: float = 0.0,
        height: float | None = None,
    ) -> list[dict[str, Any]]:
        if not isinstance(positions, list):
            raise TypeError("positions must be a list")

        columns = []

        for index, position in enumerate(positions):
            x = float(position["x"])
            y = float(position["y"])
            width = float(position.get("width", self.default_width))
            depth = float(position.get("depth", self.default_depth))
            column_height = float(
                height if height is not None
                else position.get("height", self.default_height)
            )

            if min(width, depth, column_height) <= 0:
                raise ValueError("Column dimensions must be positive")

            columns.append({
                "id": str(position.get("id", f"column_{index + 1}")),
                "type": "column",
                "position": [x, y],
                "width": width,
                "depth": depth,
                "height": column_height,
                "elevation": float(floor_elevation),
                "material": position.get(
                    "material", "reinforced_concrete"
                ),
                "unit": "mm",
            })

        return columns
