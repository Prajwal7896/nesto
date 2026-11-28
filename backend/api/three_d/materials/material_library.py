"""Predefined architectural material library."""

from .material_models import Material


class MaterialLibrary:

    MATERIALS = {
        "concrete": {
            "category": "structure",
            "color": "#999999",
            "roughness": 0.9,
            "metalness": 0.0
        },
        "brick": {
            "category": "wall",
            "color": "#A64B35",
            "roughness": 0.95,
            "metalness": 0.0
        },
        "plaster": {
            "category": "wall",
            "color": "#E8E1D5",
            "roughness": 0.85,
            "metalness": 0.0
        },
        "wood": {
            "category": "furniture",
            "color": "#8B5A2B",
            "roughness": 0.75,
            "metalness": 0.0
        },
        "marble": {
            "category": "floor",
            "color": "#E5E2DC",
            "roughness": 0.25,
            "metalness": 0.0
        },
        "ceramic_tile": {
            "category": "floor",
            "color": "#C9C9C9",
            "roughness": 0.3,
            "metalness": 0.0
        },
        "glass": {
            "category": "transparent",
            "color": "#B9E5F5",
            "roughness": 0.05,
            "metalness": 0.0,
            "opacity": 0.35,
            "transparent": True
        },
        "steel": {
            "category": "metal",
            "color": "#71797E",
            "roughness": 0.3,
            "metalness": 0.85
        },
        "aluminium": {
            "category": "metal",
            "color": "#BFC5C9",
            "roughness": 0.25,
            "metalness": 0.9
        },
        "grass": {
            "category": "landscape",
            "color": "#4D8B42",
            "roughness": 1.0,
            "metalness": 0.0
        },
        "roof_tile": {
            "category": "roof",
            "color": "#9C5140",
            "roughness": 0.8,
            "metalness": 0.0
        },
        "paint_white": {
            "category": "paint",
            "color": "#F5F5F0",
            "roughness": 0.6,
            "metalness": 0.0
        },
        "paint_grey": {
            "category": "paint",
            "color": "#777777",
            "roughness": 0.6,
            "metalness": 0.0
        },
        "water": {
            "category": "liquid",
            "color": "#2196D2",
            "roughness": 0.1,
            "metalness": 0.0,
            "opacity": 0.55,
            "transparent": True
        }
    }

    @classmethod
    def get(cls, name):
        key = name.lower().strip()

        if key not in cls.MATERIALS:
            raise ValueError(f"Unknown material: {name}")

        return Material(name=key, **cls.MATERIALS[key])

    @classmethod
    def get_all(cls):
        return {
            name: Material(name=name, **properties).to_dict()
            for name, properties in cls.MATERIALS.items()
        }

    @classmethod
    def get_by_category(cls, category):
        return {
            name: Material(name=name, **properties).to_dict()
            for name, properties in cls.MATERIALS.items()
            if properties["category"] == category
        }

    @classmethod
    def register(cls, material):
        if not isinstance(material, Material):
            raise TypeError("Expected a Material instance")

        result = material.validate()

        if not result["valid"]:
            raise ValueError(result["errors"])

        cls.MATERIALS[material.name.lower()] = {
            "category": material.category,
            "color": material.color,
            "roughness": material.roughness,
            "metalness": material.metalness,
            "opacity": material.opacity,
            "transparent": material.transparent
        }
