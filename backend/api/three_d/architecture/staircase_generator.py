
from __future__ import annotations

from typing import Any


class StaircaseGenerator:
    """Generates staircase geometry specifications.

    The output describes individual steps and the staircase footprint.
    """

    def __init__(
        self,
        default_riser: float = 175.0,
        default_tread: float = 280.0,
        default_width: float = 1000.0,
    ):
        if min(default_riser, default_tread, default_width) <= 0:
            raise ValueError("Stair dimensions must be positive")

        self.default_riser = float(default_riser)
        self.default_tread = float(default_tread)
        self.default_width = float(default_width)

    def generate(
        self,
        feature: dict[str, Any],
        floor_height: float = 3000.0,
    ) -> dict[str, Any]:
        floor_height = float(floor_height)

        if floor_height <= 0:
            raise ValueError("floor_height must be positive")

        riser = float(feature.get("riser_height", self.default_riser))
        tread = float(feature.get("tread_depth", self.default_tread))
        width = float(feature.get("stair_width", self.default_width))

        if min(riser, tread, width) <= 0:
            raise ValueError("Stair dimensions must be positive")

        step_count = int(feature.get(
            "step_count",
            round(floor_height / riser)
        ))

        if step_count < 1:
            raise ValueError("Staircase must contain at least one step")

        actual_riser = floor_height / step_count
        x = float(feature.get("x", 0.0))
        y = float(feature.get("y", 0.0))

        steps = []

        for index in range(step_count):
            steps.append({
                "id": f"stair_step_{index + 1}",
                "index": index + 1,
                "x": x,
                "y": y + index * tread,
                "elevation": index * actual_riser,
                "width": width,
                "depth": tread,
                "height": actual_riser,
            })

        return {
            "id": str(feature.get("id", "staircase")),
            "type": "staircase",
            "position": [x, y],
            "width": width,
            "length": step_count * tread,
            "floor_height": floor_height,
            "step_count": step_count,
            "riser_height": actual_riser,
            "tread_depth": tread,
            "steps": steps,
            "material": feature.get("material", "concrete"),
            "unit": "mm",
        }
