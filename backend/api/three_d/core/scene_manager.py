"""In-memory scene lifecycle and collection management."""

from __future__ import annotations

from typing import Dict, Iterable, Optional

from .scene_models import Scene, SceneFloor


class SceneManager:
    """Owns a scene and provides safe floor/component registration."""

    def __init__(self, scene: Optional[Scene] = None) -> None:
        self.scene = scene or Scene(id="nesto_scene")

    def add_floor(self, floor: SceneFloor) -> None:
        if not isinstance(floor, SceneFloor):
            raise TypeError("floor must be a SceneFloor instance.")
        if any(existing.id == floor.id for existing in self.scene.floors):
            raise ValueError(f"Floor '{floor.id}' already exists in this scene.")
        self.scene.floors.append(floor)

    def replace_floor(self, floor: SceneFloor) -> None:
        if not isinstance(floor, SceneFloor):
            raise TypeError("floor must be a SceneFloor instance.")
        for index, existing in enumerate(self.scene.floors):
            if existing.id == floor.id:
                self.scene.floors[index] = floor
                return
        self.scene.floors.append(floor)

    def get_floor(self, floor_id: str) -> Optional[SceneFloor]:
        return next(
            (floor for floor in self.scene.floors if floor.id == floor_id),
            None,
        )

    def remove_floor(self, floor_id: str) -> bool:
        original_count = len(self.scene.floors)
        self.scene.floors = [
            floor for floor in self.scene.floors if floor.id != floor_id
        ]
        return len(self.scene.floors) != original_count

    def set_metadata(self, metadata: Dict) -> None:
        if not isinstance(metadata, dict):
            raise TypeError("metadata must be a dictionary.")
        self.scene.metadata.update(metadata)

    def to_dict(self) -> Dict:
        return self.scene.to_dict()

    def clear(self) -> None:
        self.scene.floors.clear()
        self.scene.metadata.clear()
