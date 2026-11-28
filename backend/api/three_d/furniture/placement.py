from __future__ import annotations

from typing import Any

from .dimensions import FurnitureDimensions


class FurniturePlacement:
    """Validates furniture placement against room polygons."""

    @staticmethod
    def point_inside_polygon(
        x: float,
        y: float,
        polygon: list[list[float]],
    ) -> bool:
        inside = False
        j = len(polygon) - 1

        for i in range(len(polygon)):
            xi, yi = polygon[i]
            xj, yj = polygon[j]

            intersects = (
                (yi > y) != (yj > y)
                and x < (xj - xi) * (y - yi) / ((yj - yi) or 1e-12) + xi
            )

            if intersects:
                inside = not inside

            j = i

        return inside

    def fits_room(
        self,
        furniture: dict[str, Any],
        room: dict[str, Any],
    ) -> bool:
        polygon = room.get("polygon")

        if not polygon or len(polygon) < 3:
            raise ValueError("Room requires a valid polygon")

        position = furniture.get("position", [0, 0])
        x, y = float(position[0]), float(position[1])

        width, depth = FurnitureDimensions.rotated_footprint(
            float(furniture["width"]),
            float(furniture["depth"]),
            float(furniture.get("rotation", 0.0)),
        )

        corners = [
            [x - width / 2, y - depth / 2],
            [x + width / 2, y - depth / 2],
            [x + width / 2, y + depth / 2],
            [x - width / 2, y + depth / 2],
        ]

        return all(
            self.point_inside_polygon(cx, cy, polygon)
            for cx, cy in corners
        )

    def validate(
        self,
        furniture_items: list[dict[str, Any]],
        rooms: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        room_lookup = {
            str(room["id"]): room for room in rooms
        }

        results = []

        for item in furniture_items:
            room_id = str(item.get("room_id", ""))
            room = room_lookup.get(room_id)

            if room is None:
                results.append({
                    "furniture_id": item.get("id"),
                    "valid": False,
                    "reason": "Room not found",
                })
                continue

            fits = self.fits_room(item, room)

            results.append({
                "furniture_id": item.get("id"),
                "valid": fits,
                "reason": None if fits else "Furniture exceeds room boundary",
            })

        return results
