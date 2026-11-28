from __future__ import annotations

from typing import Any


class FoundationGenerator:
    """Creates foundation geometry specifications in millimetres."""

    def __init__(
        self,
        default_depth: float = 1200.0,
        default_thickness: float = 300.0,
        default_offset: float = 300.0,
    ):
        if min(default_depth, default_thickness) <= 0:
            raise ValueError("Foundation dimensions must be positive")
        if default_offset < 0:
            raise ValueError("Foundation offset cannot be negative")

        self.default_depth = float(default_depth)
        self.default_thickness = float(default_thickness)
        self.default_offset = float(default_offset)

    def generate(
        self,
        plot: dict[str, Any],
        elevation: float = 0.0,
        depth: float | None = None,
        thickness: float | None = None,
    ) -> dict[str, Any]:
        width = float(plot["width"])
        length = float(plot["height"])
        foundation_depth = float(
            self.default_depth if depth is None else depth
        )
        slab_thickness = float(
            self.default_thickness if thickness is None else thickness
        )

        if min(width, length, foundation_depth, slab_thickness) <= 0:
            raise ValueError("Foundation dimensions must be positive")

        offset = self.default_offset
        polygon = [
            [-offset, -offset],
            [width + offset, -offset],
            [width + offset, length + offset],
            [-offset, length + offset],
        ]

        return {
            "id": "main_foundation",
            "type": "foundation",
            "polygon": polygon,
            "width": width + 2 * offset,
            "length": length + 2 * offset,
            "depth": foundation_depth,
            "thickness": slab_thickness,
            "elevation": float(elevation),
            "material": "reinforced_concrete",
            "unit": "mm",
        }
