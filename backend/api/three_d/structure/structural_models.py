from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class StructuralElement:
    id: str
    element_type: str
    material: str = "reinforced_concrete"
    properties: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "element_type": self.element_type,
            "material": self.material,
            "properties": self.properties,
        }


@dataclass
class Foundation:
    id: str
    width: float
    depth: float
    thickness: float
    elevation: float
    polygon: list[list[float]]
    material: str = "reinforced_concrete"

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id, "type": "foundation",
            "width": self.width, "depth": self.depth,
            "thickness": self.thickness, "elevation": self.elevation,
            "polygon": self.polygon, "material": self.material,
            "unit": "mm",
        }


@dataclass
class Column:
    id: str
    x: float
    y: float
    width: float
    depth: float
    height: float
    elevation: float = 0.0
    material: str = "reinforced_concrete"

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id, "type": "column",
            "position": [self.x, self.y],
            "width": self.width, "depth": self.depth,
            "height": self.height, "elevation": self.elevation,
            "material": self.material, "unit": "mm",
        }


@dataclass
class Beam:
    id: str
    start: list[float]
    end: list[float]
    width: float
    height: float
    elevation: float
    material: str = "reinforced_concrete"

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id, "type": "beam",
            "start": self.start, "end": self.end,
            "width": self.width, "height": self.height,
            "elevation": self.elevation,
            "material": self.material, "unit": "mm",
        }


@dataclass
class Slab:
    id: str
    polygon: list[list[float]]
    thickness: float
    elevation: float
    material: str = "reinforced_concrete"

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id, "type": "slab",
            "polygon": self.polygon,
            "thickness": self.thickness,
            "elevation": self.elevation,
            "material": self.material, "unit": "mm",
        }
