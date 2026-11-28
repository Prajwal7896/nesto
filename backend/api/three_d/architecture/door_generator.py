
from __future__ import annotations

from typing import Any


class DoorGenerator:
    """Converts planner door definitions into 3D door specifications."""

    def __init__(
        self,
        default_height: float = 2100.0,
        default_thickness: float = 40.0,
    ):
        if default_height <= 0 or default_thickness <= 0:
            raise ValueError("Door dimensions must be positive")

        self.default_height = float(default_height)
        self.default_thickness = float(default_thickness)

    def generate(
        self,
        doors: list[dict[str, Any]],
        wall_lookup: dict[int, dict[str, Any]] | None = None,
    ) -> list[dict[str, Any]]:
        if not isinstance(doors, list):
            raise TypeError("doors must be a list")

        wall_lookup = wall_lookup or {}
        result = []

        for index, door in enumerate(doors):
            wall_index = int(door["wall"])
            width = float(door.get("width", 900.0))
            height = float(door.get("height", self.default_height))
            position = float(door.get("position", 0.5))

            if width <= 0 or height <= 0:
                raise ValueError("Door width and height must be positive")

            if not 0.0 <= position <= 1.0:
                raise ValueError("Door position must be between 0 and 1")

            wall = wall_lookup.get(wall_index)

            if wall is not None and width > float(wall["length"]):
                raise ValueError(
                    f"Door {index} is wider than its host wall"
                )

            result.append({
                "id": str(door.get("id", f"door_{index}")),
                "type": "door",
                "wall_index": wall_index,
                "position": position,
                "width": width,
                "height": height,
                "thickness": float(
                    door.get("thickness", self.default_thickness)
                ),
                "sill_height": 0.0,
                "hinge": door.get("hinge", "left"),
                "swing": door.get("swing", "inward"),
                "from_id": door.get("from_id"),
                "to_id": door.get("to_id"),
                "material": door.get("material", "wood"),
                "wall_id": wall.get("id") if wall else None,
            })

        return result
