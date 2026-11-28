
from __future__ import annotations

from typing import Any


class WindowGenerator:
    """Converts planner window definitions into 3D window specifications."""

    def __init__(
        self,
        default_height: float = 1200.0,
        default_sill_height: float = 900.0,
        default_frame_width: float = 50.0,
    ):
        if min(
            default_height,
            default_sill_height,
            default_frame_width,
        ) < 0:
            raise ValueError("Window dimensions cannot be negative")

        self.default_height = float(default_height)
        self.default_sill_height = float(default_sill_height)
        self.default_frame_width = float(default_frame_width)

    def generate(
        self,
        windows: list[dict[str, Any]],
        wall_lookup: dict[int, dict[str, Any]] | None = None,
    ) -> list[dict[str, Any]]:
        if not isinstance(windows, list):
            raise TypeError("windows must be a list")

        wall_lookup = wall_lookup or {}
        result = []

        for index, window in enumerate(windows):
            wall_index = int(window["wall"])
            width = float(window.get("width", 1200.0))
            height = float(window.get("height", self.default_height))
            sill = float(
                window.get("sill_height", self.default_sill_height)
            )
            position = float(window.get("position", 0.5))

            if width <= 0 or height <= 0:
                raise ValueError("Window width and height must be positive")

            if sill < 0:
                raise ValueError("Window sill height cannot be negative")

            if not 0.0 <= position <= 1.0:
                raise ValueError("Window position must be between 0 and 1")

            wall = wall_lookup.get(wall_index)

            if wall is not None:
                if width > float(wall["length"]):
                    raise ValueError(
                        f"Window {index} is wider than its host wall"
                    )

                wall_height = float(wall.get("height", 3000.0))
                if sill + height > wall_height:
                    raise ValueError(
                        f"Window {index} exceeds its wall height"
                    )

            result.append({
                "id": str(window.get("id", f"window_{index}")),
                "type": "window",
                "wall_index": wall_index,
                "position": position,
                "width": width,
                "height": height,
                "sill_height": sill,
                "frame_width": float(
                    window.get("frame_width", self.default_frame_width)
                ),
                "wall_id": wall.get("id") if wall else None,
                "material": window.get("material", "aluminium"),
                "glass": window.get("glass", "clear"),
            })

        return result
