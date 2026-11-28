from __future__ import annotations

from typing import Any


class FurnitureMaterials:
    """Material definitions for Three.js furniture rendering."""

    MATERIALS: dict[str, dict[str, Any]] = {
        "wood": {
            "color": "#8B5A2B",
            "roughness": 0.75,
            "metalness": 0.0,
        },
        "oak": {
            "color": "#C19A6B",
            "roughness": 0.7,
            "metalness": 0.0,
        },
        "walnut": {
            "color": "#5C4033",
            "roughness": 0.7,
            "metalness": 0.0,
        },
        "fabric": {
            "color": "#A7A7A7",
            "roughness": 0.95,
            "metalness": 0.0,
        },
        "leather": {
            "color": "#704214",
            "roughness": 0.65,
            "metalness": 0.0,
        },
        "metal": {
            "color": "#777F85",
            "roughness": 0.35,
            "metalness": 0.8,
        },
        "stone": {
            "color": "#B8B3A8",
            "roughness": 0.8,
            "metalness": 0.0,
        },
        "ceramic": {
            "color": "#F2F2F2",
            "roughness": 0.25,
            "metalness": 0.0,
        },
        "glass": {
            "color": "#B9DCEB",
            "roughness": 0.1,
            "metalness": 0.0,
            "transparent": True,
            "opacity": 0.35,
        },
    }

    @classmethod
    def get(cls, material_name: str) -> dict[str, Any]:
        material = cls.MATERIALS.get(material_name)

        if material is None:
            raise KeyError(f"Unknown furniture material: {material_name}")

        return dict(material)

    @classmethod
    def register(
        cls,
        material_name: str,
        properties: dict[str, Any],
    ) -> None:
        if "color" not in properties:
            raise ValueError("Material requires a color")

        cls.MATERIALS[material_name] = dict(properties)

    @classmethod
    def apply(
        cls,
        furniture_items: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        output = []

        for item in furniture_items:
            result = dict(item)
            material_name = str(result.get("material", "wood"))
            result["material_properties"] = cls.get(material_name)
            output.append(result)

        return output
