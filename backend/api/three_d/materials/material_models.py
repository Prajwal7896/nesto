"""Material data structures for Nesto 3D."""

from dataclasses import dataclass, asdict
from typing import Optional


@dataclass
class Material:
    name: str
    category: str
    color: str = "#FFFFFF"
    roughness: float = 0.7
    metalness: float = 0.0
    opacity: float = 1.0
    transparent: bool = False
    texture_path: Optional[str] = None
    normal_map_path: Optional[str] = None
    repeat_x: float = 1.0
    repeat_y: float = 1.0

    def to_dict(self):
        return asdict(self)

    def validate(self):
        errors = []

        if not self.name:
            errors.append("Material name is required")

        if not 0 <= self.roughness <= 1:
            errors.append("Roughness must be between 0 and 1")

        if not 0 <= self.metalness <= 1:
            errors.append("Metalness must be between 0 and 1")

        if not 0 <= self.opacity <= 1:
            errors.append("Opacity must be between 0 and 1")

        if self.repeat_x <= 0 or self.repeat_y <= 0:
            errors.append("Texture repeat values must be positive")

        return {"valid": not errors, "errors": errors}
