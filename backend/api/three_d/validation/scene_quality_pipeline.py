
from copy import deepcopy

from .room_validator import RoomGeometryValidator
from .connectivity_validator import RoomConnectivityValidator
from .furniture_clearance_validator import FurnitureClearanceValidator
from .bathroom_validator import BathroomFixtureValidator


class SceneQualityPipeline:
    """Runs scene validation and attempts conservative furniture corrections."""

    def __init__(self):
        self.room_validator = RoomGeometryValidator()
        self.connectivity_validator = RoomConnectivityValidator()
        self.furniture_validator = FurnitureClearanceValidator()
        self.bathroom_validator = BathroomFixtureValidator()

    def _get(self, obj, key, default=None):
        if isinstance(obj, dict):
            return obj.get(key, default)
        return getattr(obj, key, default)

    def _set_position(self, item, x, y):
        position = self._get(item, "position")

        if isinstance(item, dict):
            if isinstance(position, dict):
                item["position"] = {"x": x, "y": y}
            else:
                item["position"] = [x, y]
        else:
            if isinstance(position, dict):
                item.position = {"x": x, "y": y}
            else:
                item.position = [x, y]

    def _inside_polygon(self, point, polygon):
        x, y = point
        inside = False
        j = len(polygon) - 1

        for i in range(len(polygon)):
            xi, yi = polygon[i]
            xj, yj = polygon[j]

            if (yi > y) != (yj > y):
                crossing_x = (
                    (xj - xi) * (y - yi) / (yj - yi) + xi
                )
                if x < crossing_x:
                    inside = not inside

            j = i

        return inside

    def _corners(self, item, x=None, y=None):
        import math

        position = self._get(item, "position")

        if x is None or y is None:
            if isinstance(position, dict):
                x = float(position.get("x", 0))
                y = float(position.get("y", 0))
            else:
                x = float(position[0])
                y = float(position[1])

        width = float(self._get(item, "width", 0))
        depth = float(self._get(item, "depth", 0))
        rotation = float(self._get(item, "rotation", 0))

        hw = width / 2
        hd = depth / 2

        angle = math.radians(rotation)
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)

        local = [
            (-hw, -hd),
            (hw, -hd),
            (hw, hd),
            (-hw, hd)
        ]

        return [
            (
                x + px * cos_a - py * sin_a,
                y + px * sin_a + py * cos_a
            )
            for px, py in local
        ]

    def _fits_room(self, item, room, x, y):
        polygon = self._get(room, "polygon")

        if not polygon or len(polygon) < 3:
            return False

        corners = self._corners(item, x, y)

        return all(
            self._inside_polygon(point, polygon)
            for point in corners
        )

    def _overlaps_at(self, item, x, y, other):
        a = self._corners(item, x, y)
        b = self._corners(other)

        def bounds(points):
            xs = [p[0] for p in points]
            ys = [p[1] for p in points]
            return min(xs), min(ys), max(xs), max(ys)

        ax1, ay1, ax2, ay2 = bounds(a)
        bx1, by1, bx2, by2 = bounds(b)

        return (
            ax1 < bx2 and ax2 > bx1
            and ay1 < by2 and ay2 > by1
        )

    def _try_reposition(self, item, room, other_items):
        position = self._get(item, "position")

        if isinstance(position, dict):
            original_x = float(position.get("x", 0))
            original_y = float(position.get("y", 0))
        else:
            original_x = float(position[0])
            original_y = float(position[1])

        polygon = self._get(room, "polygon")

        if not polygon:
            return None

        min_x = min(point[0] for point in polygon)
        max_x = max(point[0] for point in polygon)
        min_y = min(point[1] for point in polygon)
        max_y = max(point[1] for point in polygon)

        # Search around the existing position first.
        candidates = []

        for radius in range(200, 1601, 200):
            candidates.extend([
                (original_x + radius, original_y),
                (original_x - radius, original_y),
                (original_x, original_y + radius),
                (original_x, original_y - radius),
                (original_x + radius, original_y + radius),
                (original_x - radius, original_y + radius),
                (original_x + radius, original_y - radius),
                (original_x - radius, original_y - radius),
            ])

        # Add a coarse room-grid search as a fallback.
        x = min_x + 200
        while x <= max_x - 200:
            y = min_y + 200

            while y <= max_y - 200:
                candidates.append((x, y))
                y += 200

            x += 200

        seen = set()

        for candidate_x, candidate_y in candidates:
            key = (round(candidate_x, 2), round(candidate_y, 2))

            if key in seen:
                continue

            seen.add(key)

            if not self._fits_room(
                item, room, candidate_x, candidate_y
            ):
                continue

            if any(
                self._overlaps_at(item, candidate_x, candidate_y, other)
                for other in other_items
            ):
                continue

            return candidate_x, candidate_y

        return None

    def _correct_furniture(self, floor):
        furniture = self._get(floor, "furniture", []) or []
        rooms = self._get(floor, "rooms", []) or []

        room_lookup = {
            self._get(room, "id"): room for room in rooms
        }

        changes = []
        unresolved = []

        # Work on a copy so a failed correction cannot corrupt the scene.
        working = deepcopy(furniture)

        for index, item in enumerate(working):
            room_id = self._get(item, "room_id")
            room = room_lookup.get(room_id)

            if room is None:
                unresolved.append({
                    "furniture_id": self._get(item, "id"),
                    "reason": "Assigned room was not found."
                })
                continue

            others = [
                other for other_index, other in enumerate(working)
                if other_index != index
                and self._get(other, "room_id") == room_id
            ]

            original_position = self._get(item, "position")
            if isinstance(original_position, dict):
                old_x = float(original_position.get("x", 0))
                old_y = float(original_position.get("y", 0))
            else:
                old_x = float(original_position[0])
                old_y = float(original_position[1])

            # Skip items that already fit and do not overlap.
            if (
                self._fits_room(item, room, old_x, old_y)
                and not any(
                    self._overlaps_at(item, old_x, old_y, other)
                    for other in others
                )
            ):
                continue

            new_position = self._try_reposition(item, room, others)

            if new_position is None:
                unresolved.append({
                    "furniture_id": self._get(item, "id"),
                    "reason": "No safe alternative position found."
                })
                continue

            self._set_position(item, *new_position)

            changes.append({
                "furniture_id": self._get(item, "id"),
                "room_id": room_id,
                "old_position": [old_x, old_y],
                "new_position": list(new_position)
            })

        # Commit the copy only after the correction pass completes.
        if isinstance(floor, dict):
            floor["furniture"] = working
        else:
            floor.furniture = working

        return changes, unresolved

    def validate_and_correct_floor(self, floor, auto_correct=True):
        if auto_correct:
            changes, unresolved = self._correct_furniture(floor)
        else:
            changes, unresolved = [], []

        geometry = self.room_validator.validate_floor(floor)
        connectivity = self.connectivity_validator.validate_floor(floor)
        furniture = self.furniture_validator.validate_floor(floor)
        bathroom = self.bathroom_validator.validate_floor(floor)

        reports = {
            "room_validation": geometry,
            "connectivity_validation": connectivity,
            "furniture_validation": furniture,
            "bathroom_validation": bathroom
        }

        critical_errors = (
            geometry.get("errors", [])
            + connectivity.get("errors", [])
            + furniture.get("errors", [])
            + bathroom.get("issues", [])
        )

        return {
            "floor_id": self._get(floor, "id"),
            "valid": not critical_errors,
            "auto_correction_enabled": auto_correct,
            "corrections_applied": changes,
            "unresolved_furniture_issues": unresolved,
            "reports": reports,
            "summary": {
                "corrections_count": len(changes),
                "unresolved_count": len(unresolved),
                "geometry_valid": geometry.get("valid", False),
                "connectivity_valid": connectivity.get("valid", False),
                "furniture_valid": furniture.get("valid", False),
                "bathroom_valid": bathroom.get("valid", False)
            }
        }
