from __future__ import annotations

from typing import Any


class SlabGenerator:
    """Creates floor and roof slab geometry specifications."""

    def __init__(
        self,
        default_thickness: float = 150.0,
        default_material: str = "reinforced_concrete",
    ):
        if default_thickness <= 0:
            raise ValueError("Slab thickness must be positive")

        self.default_thickness = float(default_thickness)
        self.default_material = default_material

    def generate(
        self,
        polygons: list[dict[str, Any]],
        elevation: float = 0.0,
    ) -> list[dict[str, Any]]:
        if not isinstance(polygons, list):
            raise TypeError("polygons must be a list")

        slabs = []

        for index, item in enumerate(polygons):
            polygon = item.get("polygon")

            if not isinstance(polygon, list) or len(polygon) < 3:
                raise ValueError(
                    f"Slab {index} requires a polygon with 3+ points"
                )

            points = []
            for point in polygon:
                if not isinstance(point, (list, tuple)) or len(point) != 2:
                    raise ValueError("Slab points must be [x, y]")
                points.append([float(point[0]), float(point[1])])

            thickness = float(
                item.get("thickness", self.default_thickness)
            )

            if thickness <= 0:
                raise ValueError("Slab thickness must be positive")

            slabs.append({
                "id": str(item.get("id", f"slab_{index + 1}")),
                "type": item.get("type", "floor_slab"),
                "polygon": points,
                "thickness": thickness,
                "elevation": float(item.get("elevation", elevation)),
                "material": item.get(
                    "material", self.default_material
                ),
                "unit": "mm",
            })

        return slabs
