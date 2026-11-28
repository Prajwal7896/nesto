
class FurnitureClearanceValidator:
    """Checks furniture overlaps, room boundaries and wardrobe access space."""

    WARDROBE_CLEARANCE_MM = 700.0
    TOLERANCE_MM = 1.0

    def _get(self, obj, key, default=None):
        if isinstance(obj, dict):
            return obj.get(key, default)
        return getattr(obj, key, default)

    def _position(self, item):
        position = self._get(item, "position", None)

        if isinstance(position, dict):
            return (
                float(position.get("x", 0)),
                float(position.get("y", 0))
            )

        if isinstance(position, (list, tuple)) and len(position) >= 2:
            return float(position[0]), float(position[1])

        return (
            float(self._get(item, "x", 0)),
            float(self._get(item, "y", 0))
        )

    def _corners(self, item, extra_depth=0.0):
        x, y = self._position(item)

        width = float(self._get(item, "width", 0))
        depth = float(self._get(item, "depth", 0)) + extra_depth
        rotation = float(self._get(item, "rotation", 0))

        half_w = width / 2
        half_d = depth / 2

        local = [
            (-half_w, -half_d),
            (half_w, -half_d),
            (half_w, half_d),
            (-half_w, half_d)
        ]

        import math

        angle = math.radians(rotation)
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)

        return [
            (
                x + px * cos_a - py * sin_a,
                y + px * sin_a + py * cos_a
            )
            for px, py in local
        ]

    def _aabb(self, corners):
        xs = [point[0] for point in corners]
        ys = [point[1] for point in corners]

        return min(xs), min(ys), max(xs), max(ys)

    def _overlap(self, a, b):
        ax1, ay1, ax2, ay2 = self._aabb(self._corners(a))
        bx1, by1, bx2, by2 = self._aabb(self._corners(b))

        return (
            ax1 < bx2 - self.TOLERANCE_MM
            and ax2 > bx1 + self.TOLERANCE_MM
            and ay1 < by2 - self.TOLERANCE_MM
            and ay2 > by1 + self.TOLERANCE_MM
        )

    def _point_inside_polygon(self, point, polygon):
        x, y = point
        inside = False

        if not polygon or len(polygon) < 3:
            return False

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

    def _inside_room(self, item, room):
        polygon = self._get(room, "polygon", None)

        if not polygon:
            return None

        corners = self._corners(item)

        return all(
            self._point_inside_polygon(point, polygon)
            for point in corners
        )

    def _wardrobe_access_box(self, wardrobe):
        # Access space extends from the wardrobe's local front edge.
        # The local +Y direction is used as the assumed front direction.
        x, y = self._position(wardrobe)

        width = float(self._get(wardrobe, "width", 0))
        depth = float(self._get(wardrobe, "depth", 0))
        rotation = float(self._get(wardrobe, "rotation", 0))

        half_w = width / 2
        start_y = depth / 2
        end_y = start_y + self.WARDROBE_CLEARANCE_MM

        local = [
            (-half_w, start_y),
            (half_w, start_y),
            (half_w, end_y),
            (-half_w, end_y)
        ]

        import math

        angle = math.radians(rotation)
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)

        return [
            (
                x + px * cos_a - py * sin_a,
                y + px * sin_a + py * cos_a
            )
            for px, py in local
        ]

    def _boxes_overlap(self, corners_a, corners_b):
        ax1, ay1, ax2, ay2 = self._aabb(corners_a)
        bx1, by1, bx2, by2 = self._aabb(corners_b)

        return (
            ax1 < bx2 - self.TOLERANCE_MM
            and ax2 > bx1 + self.TOLERANCE_MM
            and ay1 < by2 - self.TOLERANCE_MM
            and ay2 > by1 + self.TOLERANCE_MM
        )

    def validate_floor(self, floor):
        furniture = self._get(floor, "furniture", []) or []
        rooms = self._get(floor, "rooms", []) or []

        room_lookup = {
            self._get(room, "id"): room
            for room in rooms
            if self._get(room, "id")
        }

        errors = []
        warnings = []
        collisions = []
        boundary_issues = []
        wardrobe_access_issues = []

        # Validate dimensions and room placement.
        for item in furniture:
            item_id = self._get(item, "id", "unknown_furniture")
            room_id = self._get(item, "room_id")
            item_type = str(self._get(item, "type", "")).lower()

            width = float(self._get(item, "width", 0))
            depth = float(self._get(item, "depth", 0))
            height = float(self._get(item, "height", 0))

            if min(width, depth, height) <= 0:
                errors.append(
                    f"{item_id}: furniture has invalid dimensions."
                )
                continue

            room = room_lookup.get(room_id)

            if room is None:
                warnings.append(
                    f"{item_id}: assigned room '{room_id}' was not found."
                )
                continue

            inside = self._inside_room(item, room)

            if inside is False:
                boundary_issues.append({
                    "furniture_id": item_id,
                    "room_id": room_id,
                    "issue": "Furniture footprint extends outside room."
                })

            if inside is None:
                warnings.append(
                    f"{item_id}: room polygon is unavailable; "
                    "boundary check skipped."
                )

        # Check furniture pairs within the same room.
        for i, first in enumerate(furniture):
            for second in furniture[i + 1:]:
                first_room = self._get(first, "room_id")
                second_room = self._get(second, "room_id")

                if first_room != second_room:
                    continue

                if self._overlap(first, second):
                    collisions.append({
                        "first_id": self._get(first, "id"),
                        "second_id": self._get(second, "id"),
                        "room_id": first_room,
                        "issue": "Furniture footprints overlap."
                    })

        # Check wardrobe access clearance.
        for wardrobe in furniture:
            wardrobe_type = str(
                self._get(wardrobe, "type", "")
            ).lower()

            if "wardrobe" not in wardrobe_type:
                continue

            wardrobe_id = self._get(wardrobe, "id")
            room_id = self._get(wardrobe, "room_id")
            access_box = self._wardrobe_access_box(wardrobe)

            for other in furniture:
                if other is wardrobe:
                    continue

                if self._get(other, "room_id") != room_id:
                    continue

                if self._boxes_overlap(
                    access_box,
                    self._corners(other)
                ):
                    wardrobe_access_issues.append({
                        "wardrobe_id": wardrobe_id,
                        "blocking_furniture_id": self._get(other, "id"),
                        "room_id": room_id,
                        "required_clearance_mm": self.WARDROBE_CLEARANCE_MM
                    })

        for issue in boundary_issues:
            warnings.append(
                f"{issue['furniture_id']}: furniture extends outside "
                f"room {issue['room_id']}."
            )

        for issue in collisions:
            warnings.append(
                f"{issue['first_id']} overlaps {issue['second_id']} "
                f"in {issue['room_id']}."
            )

        for issue in wardrobe_access_issues:
            warnings.append(
                f"{issue['wardrobe_id']} access area is blocked by "
                f"{issue['blocking_furniture_id']}."
            )

        return {
            "floor_id": self._get(floor, "id"),
            "valid": not errors and not collisions and not boundary_issues
                     and not wardrobe_access_issues,
            "furniture_count": len(furniture),
            "collision_count": len(collisions),
            "boundary_issue_count": len(boundary_issues),
            "wardrobe_access_issue_count": len(wardrobe_access_issues),
            "collisions": collisions,
            "boundary_issues": boundary_issues,
            "wardrobe_access_issues": wardrobe_access_issues,
            "errors": errors,
            "warnings": warnings
        }
