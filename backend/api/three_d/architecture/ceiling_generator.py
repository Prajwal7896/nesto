
from __future__ import annotations

from typing import Any


class CeilingGenerator:
    """Generates ceiling surfaces above rooms."""

    def __init__(
        self,
        ceiling_height: float = 3000.0,
        thickness: float = 100.0,
    ):
        if ceiling_height <= 0 or thickness <= 0:
            raise ValueError("Ceiling dimensions must be positive")

        self.ceiling_height = float(ceiling_height)
        self.thickness = float(thickness)

    def generate(
        self,
        rooms: list[dict[str, Any]],
        floor_elevation: float = 0.0,
        ceiling_height: float | None = None,
    ) -> list[dict[str, Any]]:
        height = float(ceiling_height or self.ceiling_height)

        if height <= 0:
            raise ValueError("ceiling_height must be positive")

        ceilings = []

        for index, room in enumerate(rooms):
            polygon = room.get("polygon")

            if not polygon or len(polygon) < 3:
                raise ValueError(
                    f"Room {room.get('id', index)} has invalid polygon"
                )

            ceilings.append({
                "id": f"{room.get('id', index)}_ceiling",
                "room_id": str(room.get("id", index)),
                "polygon": polygon,
                "elevation": float(floor_elevation) + height,
                "thickness": self.thickness,
                "material": room.get(
                    "ceiling_material", "white_plaster"
                ),
                "type": "ceiling",
            })

        return ceilings
