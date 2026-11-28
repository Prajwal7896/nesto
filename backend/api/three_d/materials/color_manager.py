"""Color and surface appearance management."""

import re


class ColorManager:

    HEX_PATTERN = re.compile(r"^#?[0-9a-fA-F]{6}$")

    @classmethod
    def normalize(cls, color):
        if not isinstance(color, str) or not cls.HEX_PATTERN.match(color):
            raise ValueError("Color must be a six-digit HEX value")

        return "#" + color.lstrip("#").upper()

    @classmethod
    def apply_color(cls, material, color):
        if not isinstance(material, dict):
            raise TypeError("Material must be a dictionary")

        material["color"] = cls.normalize(color)
        return material

    @classmethod
    def apply_palette(cls, material, palette):
        if not isinstance(palette, dict):
            raise TypeError("Palette must be a dictionary")

        for key, color in palette.items():
            material[key] = cls.normalize(color)

        return material

    @staticmethod
    def get_default_palette():
        return {
            "wall": "#E8E1D5",
            "floor": "#C9C9C9",
            "ceiling": "#F5F5F0",
            "wood": "#8B5A2B",
            "metal": "#71797E",
            "glass": "#B9E5F5",
            "garden": "#4D8B42"
        }
