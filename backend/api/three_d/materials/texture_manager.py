"""Texture configuration manager for Three.js materials."""

from pathlib import PurePosixPath, PureWindowsPath


class TextureManager:

    SUPPORTED_FORMATS = {
        ".png", ".jpg", ".jpeg", ".webp"
    }

    @classmethod
    def configure(
        cls,
        texture_path,
        repeat_x=1.0,
        repeat_y=1.0,
        normal_map_path=None
    ):
        if not isinstance(texture_path, str) or not texture_path.strip():
            raise ValueError("A valid texture path is required")

        if repeat_x <= 0 or repeat_y <= 0:
            raise ValueError("Texture repeat values must be positive")

        extension = (
            PureWindowsPath(texture_path).suffix.lower()
            or PurePosixPath(texture_path).suffix.lower()
        )

        if extension not in cls.SUPPORTED_FORMATS:
            raise ValueError("Unsupported texture format")

        if normal_map_path is not None:
            if not isinstance(normal_map_path, str) or not normal_map_path.strip():
                raise ValueError("Normal map path must be a non-empty string")

        return {
            "map": texture_path,
            "normalMap": normal_map_path,
            "repeat": {
                "x": float(repeat_x),
                "y": float(repeat_y)
            },
            "wrapS": "RepeatWrapping",
            "wrapT": "RepeatWrapping"
        }

    @staticmethod
    def apply_to_material(material, texture_config):
        if not isinstance(material, dict):
            raise TypeError("Material must be a dictionary")

        material["texture"] = texture_config
        return material
