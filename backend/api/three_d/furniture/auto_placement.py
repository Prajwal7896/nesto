from __future__ import annotations

from .dimensions import FurnitureDimensions
from .generator import FurnitureGenerator
from .library import FurnitureLibrary


class FurnitureAutoPlacer:
    """Places catalog furniture inside rooms without boundary violations."""

    ROOM_FURNITURE = {
        "bedroom": [
            "double_bed",
            "wardrobe",
            "bedside_table",
            "bedside_table",
        ],
        "master_bedroom": [
            "queen_bed",
            "wardrobe",
            "bedside_table",
            "bedside_table",
        ],
        "living_room": [
            "sofa_3_seater",
            "coffee_table",
            "tv_unit",
        ],
        "dining_room": [
            "dining_table_4",
            "dining_chair",
            "dining_chair",
            "dining_chair",
            "dining_chair",
        ],
        "kitchen": [
            "kitchen_counter",
            "refrigerator",
            "sink",
        ],
        "bathroom": [
            "shower",
            "toilet",
            "washbasin",
        ],
    }

    def __init__(self, grid_size: float = 100.0):
        if grid_size <= 0:
            raise ValueError("grid_size must be positive")

        self.grid_size = float(grid_size)
        self.generator = FurnitureGenerator()

    @staticmethod
    def _inside_polygon(x: float, y: float, polygon: list) -> bool:
        inside = False
        j = len(polygon) - 1

        for i in range(len(polygon)):
            xi, yi = float(polygon[i][0]), float(polygon[i][1])
            xj, yj = float(polygon[j][0]), float(polygon[j][1])

            intersects = (
                (yi > y) != (yj > y)
                and x < (xj - xi) * (y - yi) / ((yj - yi) or 1e-12) + xi
            )

            if intersects:
                inside = not inside

            j = i

        return inside

    @staticmethod
    def _footprint(item: dict) -> tuple[float, float]:
        return FurnitureDimensions.rotated_footprint(
            item["width"],
            item["depth"],
            item.get("rotation", 0),
        )

    def _fits_room(self, item: dict, polygon: list) -> bool:
        x, y = item["position"]
        width, depth = self._footprint(item)

        corners = [
            (x - width / 2, y - depth / 2),
            (x + width / 2, y - depth / 2),
            (x + width / 2, y + depth / 2),
            (x - width / 2, y + depth / 2),
        ]

        return all(
            self._inside_polygon(cx, cy, polygon)
            for cx, cy in corners
        )

    def _overlaps(self, candidate: dict, placed: list[dict]) -> bool:
        cx, cy = candidate["position"]
        cw, cd = self._footprint(candidate)

        for other in placed:
            ox, oy = other["position"]
            ow, od = self._footprint(other)

            if (
                abs(cx - ox) < (cw + ow) / 2 + 50
                and abs(cy - oy) < (cd + od) / 2 + 50
            ):
                return True

        return False

    def _find_position(
        self,
        furniture_type: str,
        polygon: list,
        placed: list[dict],
    ) -> dict | None:
        definition = FurnitureLibrary.get(furniture_type)
        dimensions = FurnitureDimensions.get_dimensions(furniture_type)

        min_x = min(float(point[0]) for point in polygon)
        max_x = max(float(point[0]) for point in polygon)
        min_y = min(float(point[1]) for point in polygon)
        max_y = max(float(point[1]) for point in polygon)

        for rotation in (0.0, 90.0):
            width, depth = FurnitureDimensions.rotated_footprint(
                dimensions["width"],
                dimensions["depth"],
                rotation,
            )

            start_x = min_x + width / 2
            start_y = min_y + depth / 2

            y = start_y
            while y + depth / 2 <= max_y:
                x = start_x

                while x + width / 2 <= max_x:
                    candidate = {
                        "type": furniture_type,
                        "position": [x, y],
                        **dimensions,
                        "rotation": rotation,
                    }

                    if (
                        self._fits_room(candidate, polygon)
                        and not self._overlaps(candidate, placed)
                    ):
                        return candidate

                    x += self.grid_size

                y += self.grid_size

        return None

    @staticmethod
    def _room_types(room_type: str) -> list[str]:
        normalized = room_type.lower().strip().replace(" ", "_").replace("-", "_")

        if "bathroom" in normalized or "washroom" in normalized:
            return FurnitureAutoPlacer.ROOM_FURNITURE["bathroom"]

        if "master_bedroom" in normalized:
            return FurnitureAutoPlacer.ROOM_FURNITURE["master_bedroom"]

        if "bedroom" in normalized:
            return FurnitureAutoPlacer.ROOM_FURNITURE["bedroom"]

        if "living" in normalized:
            return FurnitureAutoPlacer.ROOM_FURNITURE["living_room"]

        if "dining" in normalized:
            return FurnitureAutoPlacer.ROOM_FURNITURE["dining_room"]

        if "kitchen" in normalized:
            return FurnitureAutoPlacer.ROOM_FURNITURE["kitchen"]

        return []

        
    def generate_for_floor(self, floor) -> tuple[list[dict], list[str]]:
        all_furniture = []
        warnings = []

        for room in floor.rooms:
            polygon = room.polygon

            if not polygon or len(polygon) < 3:
                warnings.append(
                    f"{room.id}: missing valid room polygon; furniture skipped"
                )
                continue

            room_items = self._room_types(room.type)
            placed = []

            # Step 1: Place all furniture in this room
            for furniture_type in room_items:
                candidate = self._find_position(
                    furniture_type,
                    polygon,
                    placed,
                )

                if candidate is None:
                    warnings.append(
                        f"{room.id}: could not place {furniture_type}"
                    )
                    continue

                candidate["room_id"] = room.id
                candidate["id"] = (
                    f"{room.id}:furniture:{len(placed) + 1}"
                )

                placed.append(candidate)

            # Step 2: Generate furniture exactly once per room
            if placed:
                generator_items = []

                for item in placed:
                    generator_items.append({
                        **item,
                        "position": {
                            "x": item["position"][0],
                            "y": item["position"][1],
                        },
                    })

                generated = self.generator.generate(
                    generator_items,
                    room_id=room.id,
                    elevation=floor.elevation,
                )

                all_furniture.extend(generated)

        return all_furniture, warnings
