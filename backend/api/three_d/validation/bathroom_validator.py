
class BathroomFixtureValidator:
    """Validates bathroom fixture placement and basic usability."""

    MIN_SHOWER_SIDE_MM = 800.0
    MIN_FIXTURE_CLEARANCE_MM = 150.0
    MIN_TOILET_FRONT_CLEARANCE_MM = 600.0
    MIN_SHOWER_ENTRY_CLEARANCE_MM = 600.0
    TOLERANCE_MM = 1.0

    FIXTURE_TYPES = {
        "shower",
        "toilet",
        "washbasin",
        "sink",
    }

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

    def _corners(self, item, extra_front=0.0):
        import math

        x, y = self._position(item)
        width = float(self._get(item, "width", 0))
        depth = float(self._get(item, "depth", 0))
        rotation = float(self._get(item, "rotation", 0))

        half_w = width / 2
        half_d = depth / 2

        # Local +Y is treated as the fixture's front direction.
        local = [
            (-half_w, -half_d),
            (half_w, -half_d),
            (half_w, half_d + extra_front),
            (-half_w, half_d + extra_front)
        ]

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
        xs = [p[0] for p in corners]
        ys = [p[1] for p in corners]
        return min(xs), min(ys), max(xs), max(ys)

    def _overlap(self, corners_a, corners_b):
        ax1, ay1, ax2, ay2 = self._aabb(corners_a)
        bx1, by1, bx2, by2 = self._aabb(corners_b)

        return (
            ax1 < bx2 - self.TOLERANCE_MM
            and ax2 > bx1 + self.TOLERANCE_MM
            and ay1 < by2 - self.TOLERANCE_MM
            and ay2 > by1 + self.TOLERANCE_MM
        )

    def _point_inside_polygon(self, point, polygon):
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

    def _inside_room(self, item, room):
        polygon = self._get(room, "polygon", None)

        if not polygon or len(polygon) < 3:
            return None

        return all(
            self._point_inside_polygon(point, polygon)
            for point in self._corners(item)
        )

    def _fixture_type(self, item):
        item_type = str(self._get(item, "type", "")).lower()
        return item_type if item_type in self.FIXTURE_TYPES else None

    def validate_floor(self, floor):
        rooms = self._get(floor, "rooms", []) or []
        furniture = self._get(floor, "furniture", []) or []

        bathroom_rooms = [
            room for room in rooms
            if "bathroom" in str(
                self._get(room, "type", "")
            ).lower()
        ]

        room_lookup = {
            self._get(room, "id"): room
            for room in bathroom_rooms
        }

        issues = []
        warnings = []
        bathroom_reports = []

        for room in bathroom_rooms:
            room_id = self._get(room, "id")
            fixtures = [
                item for item in furniture
                if self._get(item, "room_id") == room_id
                and self._fixture_type(item)
            ]

            room_issues = []
            room_warnings = []

            if not fixtures:
                room_warnings.append(
                    "No bathroom fixtures were found in this room."
                )

            fixture_types = {
                self._fixture_type(item) for item in fixtures
            }

            for item in fixtures:
                item_id = self._get(item, "id", "unknown_fixture")
                item_type = self._fixture_type(item)

                width = float(self._get(item, "width", 0))
                depth = float(self._get(item, "depth", 0))
                height = float(self._get(item, "height", 0))

                if min(width, depth, height) <= 0:
                    room_issues.append(
                        f"{item_id}: invalid fixture dimensions."
                    )
                    continue

                inside = self._inside_room(item, room)

                if inside is False:
                    room_issues.append(
                        f"{item_id}: fixture extends outside the bathroom."
                    )
                elif inside is None:
                    room_warnings.append(
                        f"{item_id}: bathroom polygon unavailable; "
                        "boundary check skipped."
                    )

                if item_type == "shower":
                    if min(width, depth) < self.MIN_SHOWER_SIDE_MM:
                        room_warnings.append(
                            f"{item_id}: shower footprint is smaller than "
                            f"{self.MIN_SHOWER_SIDE_MM:.0f} mm on at least "
                            "one side."
                        )

            # Check fixture-to-fixture overlap and close spacing.
            for i, first in enumerate(fixtures):
                for second in fixtures[i + 1:]:
                    first_corners = self._corners(first)
                    second_corners = self._corners(second)

                    if self._overlap(first_corners, second_corners):
                        room_issues.append(
                            f"{self._get(first, 'id')} overlaps "
                            f"{self._get(second, 'id')}."
                        )

            # Check basic front access to toilets and showers.
            for item in fixtures:
                item_type = self._fixture_type(item)

                if item_type == "toilet":
                    clearance = self.MIN_TOILET_FRONT_CLEARANCE_MM
                elif item_type == "shower":
                    clearance = self.MIN_SHOWER_ENTRY_CLEARANCE_MM
                else:
                    continue

                access_corners = self._corners(
                    item,
                    extra_front=clearance
                )

                for other in fixtures:
                    if other is item:
                        continue

                    if self._overlap(
                        access_corners,
                        self._corners(other)
                    ):
                        room_warnings.append(
                            f"{self._get(item, 'id')} may have blocked "
                            f"front access due to "
                            f"{self._get(other, 'id')}."
                        )

            if "shower" not in fixture_types:
                room_warnings.append("No shower fixture found.")

            if "toilet" not in fixture_types:
                room_warnings.append("No toilet fixture found.")

            if "washbasin" not in fixture_types:
                room_warnings.append("No washbasin fixture found.")

            issues.extend(
                f"{room_id}: {message}" for message in room_issues
            )
            warnings.extend(
                f"{room_id}: {message}" for message in room_warnings
            )

            bathroom_reports.append({
                "room_id": room_id,
                "fixture_count": len(fixtures),
                "fixture_types": sorted(fixture_types),
                "valid": not room_issues,
                "issues": room_issues,
                "warnings": room_warnings
            })

        # Identify bathroom fixtures assigned to non-bathroom rooms.
        for item in furniture:
            if not self._fixture_type(item):
                continue

            room_id = self._get(item, "room_id")

            if room_id not in room_lookup:
                assigned_room = next(
                    (
                        room for room in rooms
                        if self._get(room, "id") == room_id
                    ),
                    None
                )

                if assigned_room is not None:
                    assigned_type = str(
                        self._get(assigned_room, "type", "")
                    ).lower()

                    if "bathroom" not in assigned_type:
                        warnings.append(
                            f"{self._get(item, 'id')}: bathroom fixture "
                            f"is assigned to non-bathroom room {room_id}."
                        )

        return {
            "floor_id": self._get(floor, "id"),
            "valid": not issues,
            "bathroom_count": len(bathroom_rooms),
            "bathroom_reports": bathroom_reports,
            "issues": issues,
            "warnings": warnings
        }
