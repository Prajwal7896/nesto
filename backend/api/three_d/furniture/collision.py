from __future__ import annotations

from typing import Any

from .dimensions import FurnitureDimensions


class FurnitureCollision:
    """Detects 2D footprint collisions between furniture items."""

    @staticmethod
    def get_bounds(
        item: dict[str, Any],
    ) -> tuple[float, float, float, float]:
        x, y = map(float, item["position"])

        width, depth = FurnitureDimensions.rotated_footprint(
            float(item["width"]),
            float(item["depth"]),
            float(item.get("rotation", 0.0)),
        )

        return (
            x - width / 2,
            y - depth / 2,
            x + width / 2,
            y + depth / 2,
        )

    def intersects(
        self,
        first: dict[str, Any],
        second: dict[str, Any],
    ) -> bool:
        if first.get("room_id") != second.get("room_id"):
            return False

        a_min_x, a_min_y, a_max_x, a_max_y = self.get_bounds(first)
        b_min_x, b_min_y, b_max_x, b_max_y = self.get_bounds(second)

        return (
            a_min_x < b_max_x
            and a_max_x > b_min_x
            and a_min_y < b_max_y
            and a_max_y > b_min_y
        )

    def detect(
        self,
        furniture_items: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        collisions = []

        for i, first in enumerate(furniture_items):
            for second in furniture_items[i + 1:]:
                if self.intersects(first, second):
                    collisions.append({
                        "first_id": first.get("id"),
                        "second_id": second.get("id"),
                        "room_id": first.get("room_id"),
                        "type": "furniture_overlap",
                    })

        return collisions
