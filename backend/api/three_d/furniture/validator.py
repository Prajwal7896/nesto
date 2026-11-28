from __future__ import annotations

from typing import Any

from .collision import FurnitureCollision
from .placement import FurniturePlacement


class FurnitureValidator:
    """Validates furniture dimensions, placement and collisions."""

    def __init__(self):
        self.placement = FurniturePlacement()
        self.collision = FurnitureCollision()

    def validate(
        self,
        furniture_items: list[dict[str, Any]],
        rooms: list[dict[str, Any]],
    ) -> dict[str, Any]:
        errors = []
        warnings = []

        for item in furniture_items:
            for field in ("width", "depth", "height"):
                try:
                    value = float(item[field])
                    if value <= 0:
                        errors.append(
                            f"{item.get('id')}: {field} must be positive"
                        )
                except (KeyError, TypeError, ValueError):
                    errors.append(
                        f"{item.get('id')}: invalid or missing {field}"
                    )

            position = item.get("position")
            if (
                not isinstance(position, (list, tuple))
                or len(position) != 2
            ):
                errors.append(
                    f"{item.get('id')}: position must be [x, y]"
                )

        placement_results = self.placement.validate(
            furniture_items, rooms
        )

        for result in placement_results:
            if not result["valid"]:
                errors.append(
                    f"{result['furniture_id']}: {result['reason']}"
                )

        collisions = self.collision.detect(furniture_items)

        for collision in collisions:
            warnings.append(
                f"{collision['first_id']} overlaps "
                f"{collision['second_id']}"
            )

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "collisions": collisions,
            "furniture_count": len(furniture_items),
        }
