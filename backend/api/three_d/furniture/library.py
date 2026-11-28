from __future__ import annotations

from typing import Any


class FurnitureLibrary:
    """Catalog of standard furniture dimensions in millimetres."""

    CATALOG: dict[str, dict[str, Any]] = {
        "single_bed": {
            "width": 1000, "depth": 2000, "height": 500,
            "material": "wood", "category": "bedroom",
        },
        "double_bed": {
            "width": 1500, "depth": 2000, "height": 500,
            "material": "wood", "category": "bedroom",
        },
        "queen_bed": {
            "width": 1600, "depth": 2000, "height": 550,
            "material": "wood", "category": "bedroom",
        },
        "king_bed": {
            "width": 1800, "depth": 2000, "height": 550,
            "material": "wood", "category": "bedroom",
        },
        "wardrobe": {
            "width": 1800, "depth": 600, "height": 2100,
            "material": "wood", "category": "bedroom",
        },
        "bedside_table": {
            "width": 500, "depth": 450, "height": 550,
            "material": "wood", "category": "bedroom",
        },
        "sofa_2_seater": {
            "width": 1600, "depth": 850, "height": 850,
            "material": "fabric", "category": "living",
        },
        "sofa_3_seater": {
            "width": 2200, "depth": 900, "height": 850,
            "material": "fabric", "category": "living",
        },
        "sofa_l_shape": {
            "width": 2800, "depth": 2000, "height": 850,
            "material": "fabric", "category": "living",
        },
        "coffee_table": {
            "width": 1000, "depth": 600, "height": 450,
            "material": "wood", "category": "living",
        },
        "tv_unit": {
            "width": 1800, "depth": 400, "height": 550,
            "material": "wood", "category": "living",
        },
        "dining_table_4": {
            "width": 1200, "depth": 800, "height": 750,
            "material": "wood", "category": "dining",
        },
        "dining_table_6": {
            "width": 1800, "depth": 900, "height": 750,
            "material": "wood", "category": "dining",
        },
        "dining_chair": {
            "width": 450, "depth": 500, "height": 900,
            "material": "wood", "category": "dining",
        },
        "study_table": {
            "width": 1200, "depth": 600, "height": 750,
            "material": "wood", "category": "study",
        },
        "office_chair": {
            "width": 600, "depth": 600, "height": 1100,
            "material": "fabric", "category": "study",
        },
        "kitchen_counter": {
            "width": 1800, "depth": 600, "height": 900,
            "material": "stone", "category": "kitchen",
        },
        "refrigerator": {
            "width": 700, "depth": 700, "height": 1800,
            "material": "metal", "category": "kitchen",
        },
        "sink": {
            "width": 600, "depth": 500, "height": 850,
            "material": "ceramic", "category": "kitchen",
        },
        "toilet": {
            "width": 400, "depth": 700, "height": 400,
            "material": "ceramic", "category": "bathroom",
        },
        "washbasin": {
            "width": 550, "depth": 450, "height": 850,
            "material": "ceramic", "category": "bathroom",
        },
        "shower": {
            "width": 900, "depth": 900, "height": 2100,
            "material": "glass", "category": "bathroom",
        },
    }

    @classmethod
    def get(cls, furniture_type: str) -> dict[str, Any]:
        item = cls.CATALOG.get(furniture_type)
        if item is None:
            raise KeyError(
                f"Unknown furniture type: {furniture_type}"
            )
        return dict(item)

    @classmethod
    def list_types(cls, category: str | None = None) -> list[str]:
        return [
            name for name, item in cls.CATALOG.items()
            if category is None or item["category"] == category
        ]

    @classmethod
    def register(
        cls,
        furniture_type: str,
        definition: dict[str, Any],
    ) -> None:
        required = {"width", "depth", "height", "material", "category"}
        missing = required - definition.keys()

        if missing:
            raise ValueError(
                f"Missing furniture properties: {sorted(missing)}"
            )

        if min(
            float(definition["width"]),
            float(definition["depth"]),
            float(definition["height"]),
        ) <= 0:
            raise ValueError("Furniture dimensions must be positive")

        cls.CATALOG[furniture_type] = dict(definition)
