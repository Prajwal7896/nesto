from __future__ import annotations

from typing import Any

from .dimensions import FurnitureDimensions


class FurnitureOptimizer:
    """Finds non-overlapping candidate positions in rectangular rooms."""

    def __init__(self, grid_size: float = 100.0):
        if grid_size <= 0:
            raise ValueError("grid_size must be positive")

        self.grid_size = float(grid_size)

    @staticmethod
    def _overlaps(
        a: dict[str, Any],
        b: dict[str, Any],
    ) -> bool:
        ax, ay = a["position"]
        bx, by = b["position"]

        aw, ad = FurnitureDimensions.rotated_footprint(
            a["width"], a["depth"], a.get("rotation", 0)
        )
        bw, bd = FurnitureDimensions.rotated_footprint(
            b["width"], b["depth"], b.get("rotation", 0)
        )

        return (
            abs(ax - bx) < (aw + bw) / 2
            and abs(ay - by) < (ad + bd) / 2
        )

    def optimize(
        self,
        furniture_items: list[dict[str, Any]],
        room: dict[str, Any],
    ) -> list[dict[str, Any]]:
        polygon = room.get("polygon")

        if not polygon or len(polygon) < 3:
            raise ValueError("Optimizer requires a room polygon")

        min_x = min(float(p[0]) for p in polygon)
        max_x = max(float(p[0]) for p in polygon)
        min_y = min(float(p[1]) for p in polygon)
        max_y = max(float(p[1]) for p in polygon)

        placed: list[dict[str, Any]] = []
        output = []

        for item in furniture_items:
            candidate = dict(item)
            width = float(candidate["width"])
            depth = float(candidate["depth"])

            selected = None

            y = min_y + depth / 2
            while y + depth / 2 <= max_y:
                x = min_x + width / 2

                while x + width / 2 <= max_x:
                    trial = dict(candidate)
                    trial["position"] = [x, y]

                    if not any(
                        self._overlaps(trial, other)
                        for other in placed
                    ):
                        selected = trial
                        break

                    x += self.grid_size

                if selected is not None:
                    break

                y += self.grid_size

            if selected is None:
                candidate["placement_status"] = "unplaced"
            else:
                candidate = selected
                candidate["placement_status"] = "placed"
                placed.append(candidate)

            output.append(candidate)

        return output
