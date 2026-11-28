from typing import Any, Dict, List, Tuple


class RoomGeometryValidator:
    def __init__(
        self,
        minimum_area_mm2: float = 1_000_000,
        boundary_tolerance_mm: float = 10.0
    ):
        self.minimum_area_mm2 = minimum_area_mm2
        self.boundary_tolerance_mm = boundary_tolerance_mm

    @staticmethod
    def _get(obj: Any, key: str, default=None):
        if isinstance(obj, dict):
            return obj.get(key, default)

        return getattr(obj, key, default)

    @staticmethod
    def _polygon_area(points: List[Tuple[float, float]]) -> float:
        area = 0.0
        count = len(points)

        for i in range(count):
            x1, y1 = points[i]
            x2, y2 = points[(i + 1) % count]
            area += x1 * y2 - x2 * y1

        return abs(area) / 2.0

    @staticmethod
    def _orientation(a, b, c):
        return (
            (b[0] - a[0]) * (c[1] - a[1])
            - (b[1] - a[1]) * (c[0] - a[0])
        )

    @classmethod
    def _segments_intersect(cls, a, b, c, d):
        eps = 1e-9

        o1 = cls._orientation(a, b, c)
        o2 = cls._orientation(a, b, d)
        o3 = cls._orientation(c, d, a)
        o4 = cls._orientation(c, d, b)

        return (
            ((o1 > eps and o2 < -eps) or
             (o1 < -eps and o2 > eps))
            and
            ((o3 > eps and o4 < -eps) or
             (o3 < -eps and o4 > eps))
        )

    @classmethod
    def _has_self_intersection(cls, points):
        count = len(points)

        for i in range(count):
            a = points[i]
            b = points[(i + 1) % count]

            for j in range(i + 1, count):
                # Adjacent edges share an endpoint intentionally.
                if j == i:
                    continue

                if j == (i + 1) % count:
                    continue

                if (j + 1) % count == i:
                    continue

                c = points[j]
                d = points[(j + 1) % count]

                if cls._segments_intersect(a, b, c, d):
                    return True

        return False

    def _normalize_polygon(self, polygon):
        if not isinstance(polygon, (list, tuple)):
            return None

        points = []

        try:
            for point in polygon:
                if not isinstance(point, (list, tuple)):
                    return None

                if len(point) < 2:
                    return None

                x = float(point[0])
                y = float(point[1])

                points.append((x, y))

        except (TypeError, ValueError, IndexError):
            return None

        # Remove repeated closing vertex.
        if len(points) >= 2 and points[0] == points[-1]:
            points.pop()

        # Remove consecutive duplicate vertices.
        cleaned = []

        for point in points:
            if not cleaned or point != cleaned[-1]:
                cleaned.append(point)

        return cleaned if len(cleaned) >= 3 else None

    def _check_floor_bounds(self, polygon, floor):
        plot_width = float(
            self._get(floor, "plot_width", 0) or 0
        )
        plot_depth = float(
            self._get(floor, "plot_depth", 0) or 0
        )

        if plot_width <= 0 or plot_depth <= 0:
            return None

        tolerance = self.boundary_tolerance_mm

        for x, y in polygon:
            if (
                x < -tolerance
                or y < -tolerance
                or x > plot_width + tolerance
                or y > plot_depth + tolerance
            ):
                return (
                    f"Room extends outside floor boundary "
                    f"({plot_width:.0f} × {plot_depth:.0f} mm)."
                )

        return None

    def validate_room(self, room, floor=None) -> Dict[str, Any]:
        room_id = self._get(room, "id", "unknown")
        room_type = self._get(room, "type", "unknown")

        errors = []
        warnings = []

        polygon = self._normalize_polygon(
            self._get(room, "polygon", None)
        )

        if polygon is None:
            errors.append("Missing or invalid room polygon.")

            return {
                "room_id": room_id,
                "room_type": room_type,
                "valid": False,
                "errors": errors,
                "warnings": warnings
            }

        area = self._polygon_area(polygon)

        if area <= 0:
            errors.append("Room polygon has zero area.")

        elif area < self.minimum_area_mm2:
            warnings.append(
                f"Room area is unusually small: {area:.0f} mm²."
            )

        if self._has_self_intersection(polygon):
            errors.append(
                "Room polygon contains self-intersecting edges."
            )

        if floor is not None:
            boundary_error = self._check_floor_bounds(
                polygon, floor
            )

            if boundary_error:
                errors.append(boundary_error)

        width = float(self._get(room, "width", 0) or 0)
        depth = float(self._get(room, "depth", 0) or 0)

        if width <= 0 or depth <= 0:
            warnings.append(
                "Room width or depth is missing or invalid."
            )

        return {
            "room_id": room_id,
            "room_type": room_type,
            "valid": len(errors) == 0,
            "area_mm2": round(area, 2),
            "errors": errors,
            "warnings": warnings
        }

    def validate_floor(self, floor) -> Dict[str, Any]:
        rooms = self._get(floor, "rooms", []) or []

        results = []
        errors = []
        warnings = []
        seen_ids = set()

        for room in rooms:
            result = self.validate_room(room, floor)
            room_id = result["room_id"]

            if room_id in seen_ids:
                result["valid"] = False
                result["errors"].append(
                    "Duplicate room ID detected."
                )

            seen_ids.add(room_id)

            results.append(result)

            for error in result["errors"]:
                errors.append({
                    "room_id": room_id,
                    "message": error
                })

            for warning in result["warnings"]:
                warnings.append({
                    "room_id": room_id,
                    "message": warning
                })

        invalid_count = sum(
            1 for result in results if not result["valid"]
        )

        return {
            "floor_id": self._get(floor, "id", "unknown"),
            "valid": invalid_count == 0,
            "total_rooms": len(rooms),
            "valid_rooms": len(rooms) - invalid_count,
            "invalid_rooms": invalid_count,
            "errors": errors,
            "warnings": warnings,
            "rooms": results
        }