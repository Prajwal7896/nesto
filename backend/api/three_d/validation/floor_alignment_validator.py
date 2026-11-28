
from __future__ import annotations

from typing import Any


class FloorAlignmentValidator:
    """Checks room and footprint alignment between consecutive floors."""

    def validate(self, floors: list) -> dict[str, Any]:
        if len(floors) < 2:
            return {
                "valid": True,
                "issues": [],
            }

        issues = []

        base_floor = floors[0]

        for upper_floor in floors[1:]:
            for room in upper_floor.rooms:
                polygon = room.polygon or []

                if len(polygon) < 3:
                    issues.append({
                        "floor": upper_floor.id,
                        "room": room.id,
                        "issue": "Invalid room polygon",
                    })
                    continue

                min_x = min(p[0] for p in polygon)
                max_x = max(p[0] for p in polygon)
                min_y = min(p[1] for p in polygon)
                max_y = max(p[1] for p in polygon)

                # Check whether the upper-floor room extends
                # beyond the ground-floor plot boundary.
                if (
                    min_x < 0
                    or min_y < 0
                    or max_x > base_floor.plot_width
                    or max_y > base_floor.plot_depth
                ):
                    issues.append({
                        "floor": upper_floor.id,
                        "room": room.id,
                        "issue": "Room extends outside building plot",
                        "bounds": [
                            min_x, min_y, max_x, max_y
                        ],
                    })

        return {
            "valid": len(issues) == 0,
            "issues": issues,
        }
