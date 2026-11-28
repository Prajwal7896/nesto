from __future__ import annotations

from typing import Any
import math


class BeamGenerator:
    """Creates horizontal beam geometry specifications."""

    def __init__(
        self,
        default_width: float = 230.0,
        default_height: float = 450.0,
    ):
        if min(default_width, default_height) <= 0:
            raise ValueError("Beam dimensions must be positive")

        self.default_width = float(default_width)
        self.default_height = float(default_height)

    def generate(
        self,
        connections: list[dict[str, Any]],
        elevation: float = 3000.0,
    ) -> list[dict[str, Any]]:
        if not isinstance(connections, list):
            raise TypeError("connections must be a list")

        beams = []

        for index, connection in enumerate(connections):
            start = connection.get("start")
            end = connection.get("end")

            if (
                not isinstance(start, (list, tuple))
                or not isinstance(end, (list, tuple))
                or len(start) != 2
                or len(end) != 2
            ):
                raise ValueError(
                    f"Beam {index} requires 2D start and end coordinates"
                )

            start = [float(start[0]), float(start[1])]
            end = [float(end[0]), float(end[1])]

            length = math.hypot(
                end[0] - start[0],
                end[1] - start[1],
            )

            if length <= 0:
                raise ValueError(f"Beam {index} has zero length")

            width = float(connection.get("width", self.default_width))
            height = float(connection.get("height", self.default_height))

            if min(width, height) <= 0:
                raise ValueError("Beam dimensions must be positive")

            beams.append({
                "id": str(connection.get("id", f"beam_{index + 1}")),
                "type": "beam",
                "start": start,
                "end": end,
                "length": length,
                "width": width,
                "height": height,
                "elevation": float(connection.get("elevation", elevation)),
                "material": connection.get(
                    "material", "reinforced_concrete"
                ),
                "unit": "mm",
            })

        return beams
