"""Nesto 3D scene-generation foundation.

This package converts Nesto's existing 2D layout dictionaries into a
renderer-independent 3D scene description. It does not modify the 2D pipeline.
"""

from .core.scene_builder import SceneBuilder, build_scene
from .core.scene_models import Scene, SceneFloor, SceneRoom, SceneWall, SceneOpening

__all__ = [
    "SceneBuilder",
    "build_scene",
    "Scene",
    "SceneFloor",
    "SceneRoom",
    "SceneWall",
    "SceneOpening",
]
