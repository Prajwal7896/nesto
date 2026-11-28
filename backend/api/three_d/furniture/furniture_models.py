from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Furniture:
    id: str
    furniture_type: str
    room_id: str
    x: float
    y: float
    width: float
    depth: float
    height: float
    rotation: float = 0.0
    elevation: float = 0.0
    material: str = "wood"
    properties: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "type": self.furniture_type,
            "room_id": self.room_id,
            "position": [self.x, self.y],
            "width": self.width,
            "depth": self.depth,
            "height": self.height,
            "rotation": self.rotation,
            "elevation": self.elevation,
            "material": self.material,
            "properties": self.properties,
            "unit": "mm",
        }
