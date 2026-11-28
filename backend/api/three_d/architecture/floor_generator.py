
from __future__ import annotations

from typing import Any


class FloorGenerator:
    """Generates floor slabs and individual room floor surfaces."""

    def __init__(
        self,
        slab_thickness: float = 150.0,
        default_material: str = "concrete",
    ):
        if slab_thickness <= 0:
            raise ValueError("slab_thickness must be positive")

        self.slab_thickness = float(slab_thickness)
        self.default_material = default_material

    def generate(
        self,
        plot: dict[str, Any],
        rooms: list[dict[str, Any]],
        elevation: float = 0.0,
    ) -> dict[str, Any]:
        width = float(plot["width"])
        depth = float(plot["height"])

        if width <= 0 or depth <= 0:
            raise ValueError("Plot dimensions must be positive")

        room_surfaces = []

        for index, room in enumerate(rooms):
            polygon = room.get("polygon")
            if not polygon or len(polygon) < 3:
                raise ValueError(
                    f"Room {room.get('id', index)} has no valid polygon"
                )

            room_surfaces.append({
                "id": f"{room.get('id', index)}_floor",
                "room_id": str(room.get("id", index)),
                "polygon": polygon,
                "elevation": float(elevation),
                "thickness": self.slab_thickness,
                "material": room.get(
                    "floor_material", self.default_material
                ),
            })

        return {
            "id": f"floor_{elevation}",
            "type": "floor_slab",
            "width": width,
            "depth": depth,
            "elevation": float(elevation),
            "thickness": self.slab_thickness,
            "material": self.default_material,
            "room_surfaces": room_surfaces,
            "unit": "mm",
        }
