from __future__ import annotations

from typing import Any

from .dimensions import FurnitureDimensions
from .library import FurnitureLibrary


class FurnitureGenerator:
    """Generates furniture geometry specifications."""

    def generate(
        self,
        furniture_items: list[dict[str, Any]],
        room_id: str | None = None,
        elevation: float = 0.0,
    ) -> list[dict[str, Any]]:
        if not isinstance(furniture_items, list):
            raise TypeError("furniture_items must be a list")

        output = []

        for index, item in enumerate(furniture_items):
            furniture_type = str(item["type"])
            definition = FurnitureLibrary.get(furniture_type)

            dimensions = FurnitureDimensions.get_dimensions(
                furniture_type,
                item.get("dimensions"),
            )

            position = item.get("position", {})
            x = float(position.get("x", item.get("x", 0.0)))
            y = float(position.get("y", item.get("y", 0.0)))
            rotation = float(item.get("rotation", 0.0))

            output.append({
                "id": str(item.get("id", f"furniture_{index + 1}")),
                "type": furniture_type,
                "category": definition["category"],
                "room_id": str(item.get("room_id", room_id or "")),
                "position": [x, y],
                **dimensions,
                "rotation": rotation,
                "elevation": float(item.get("elevation", elevation)),
                "material": item.get(
                    "material", definition["material"]
                ),
                "properties": dict(item.get("properties", {})),
                "unit": "mm",
            })

        return output
