
from __future__ import annotations

from typing import Any


class ArchitecturalDetailsGenerator:
    """Creates optional architectural detail specifications.

    Supported details:
    - skirting
    - cornice
    - lintel
    - sill
    - parapet
    - wall_trim
    """

    SUPPORTED_DETAILS = {
        "skirting",
        "cornice",
        "lintel",
        "sill",
        "parapet",
        "wall_trim",
    }

    def __init__(
        self,
        default_material: str = "plaster",
    ):
        self.default_material = default_material

    def generate(
        self,
        details: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        if not isinstance(details, list):
            raise TypeError("details must be a list")

        output = []

        for index, detail in enumerate(details):
            detail_type = str(detail.get("type", "")).lower()

            if detail_type not in self.SUPPORTED_DETAILS:
                raise ValueError(
                    f"Unsupported architectural detail: {detail_type}"
                )

            dimensions = {
                "width": float(detail.get("width", 0.0)),
                "height": float(detail.get("height", 0.0)),
                "depth": float(detail.get("depth", 0.0)),
            }

            if any(value < 0 for value in dimensions.values()):
                raise ValueError(
                    "Architectural detail dimensions cannot be negative"
                )

            if not any(dimensions.values()):
                raise ValueError(
                    f"Detail {index} requires at least one dimension"
                )

            output.append({
                "id": str(detail.get("id", f"detail_{index}")),
                "type": detail_type,
                "room_id": detail.get("room_id"),
                "wall_id": detail.get("wall_id"),
                "position": [
                    float(value)
                    for value in detail.get("position", [0.0, 0.0])
                ],
                "elevation": float(detail.get("elevation", 0.0)),
                **dimensions,
                "material": detail.get(
                    "material", self.default_material
                ),
                "unit": "mm",
            })

        return output
