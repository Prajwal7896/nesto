
from __future__ import annotations

from math import hypot
from typing import Any


class ArchitecturalGeometryValidator:
    """
    Diagnostic validation for architectural room and wall geometry.

    Coordinates and dimensions are in millimetres.
    This validator does not modify the original scene.
    """

    def __init__(
        self,
        snap_tolerance: float = 10.0,
        min_general_room_dimension: float = 1800.0,
        max_room_aspect_ratio: float = 4.5,
        orthogonal_tolerance_degrees: float = 3.0,
    ):
        self.snap_tolerance = snap_tolerance
        self.min_dimension = min_general_room_dimension
        self.max_aspect_ratio = max_room_aspect_ratio
        self.orthogonal_tolerance = orthogonal_tolerance_degrees

    @staticmethod
    def get(obj: Any, key: str, default=None):
        if isinstance(obj, dict):
            return obj.get(key, default)
        return getattr(obj, key, default)

    @staticmethod
    def point(value):
        return float(value[0]), float(value[1])

    @staticmethod
    def distance(a, b):
        return hypot(a[0] - b[0], a[1] - b[1])

    @staticmethod
    def cross(a, b, c):
        return (
            (b[0] - a[0]) * (c[1] - a[1])
            - (b[1] - a[1]) * (c[0] - a[0])
        )

    def polygon_area(self, polygon):
        area = 0.0
        for i, point in enumerate(polygon):
            nxt = polygon[(i + 1) % len(polygon)]
            area += point[0] * nxt[1] - nxt[0] * point[1]
        return abs(area) / 2.0

    def validate_room(self, room):
        room_id = self.get(room, "id", "unknown")
        polygon = self.get(room, "polygon", []) or []
        warnings = []
        errors = []

        if len(polygon) < 3:
            errors.append(
                f"Room {room_id}: boundary has fewer than three vertices."
            )
            return {"errors": errors, "warnings": warnings}

        polygon = [self.point(p) for p in polygon]

        if len(set(polygon)) < 3:
            errors.append(
                f"Room {room_id}: boundary contains duplicate vertices."
            )

        for i in range(len(polygon)):
            a = polygon[i]
            b = polygon[(i + 1) % len(polygon)]

            if self.distance(a, b) <= 0.001:
                errors.append(
                    f"Room {room_id}: zero-length boundary edge at {i}."
                )

        area = self.polygon_area(polygon)

        if area <= 1:
            errors.append(f"Room {room_id}: invalid polygon area.")

        # Check self-intersection, excluding adjacent edges.
        n = len(polygon)

        for i in range(n):
            a = polygon[i]
            b = polygon[(i + 1) % n]

            for j in range(i + 1, n):
                if j == i:
                    continue
                if j == (i + 1) % n:
                    continue
                if i == 0 and j == n - 1:
                    continue

                c = polygon[j]
                d = polygon[(j + 1) % n]

                if self.segments_intersect(a, b, c, d):
                    errors.append(
                        f"Room {room_id}: boundary self-intersects "
                        f"between edges {i} and {j}."
                    )

        xs = [p[0] for p in polygon]
        ys = [p[1] for p in polygon]

        width = max(xs) - min(xs)
        depth = max(ys) - min(ys)

        room_type = str(
            self.get(room, "type", "")
        ).lower()

        small_room_types = (
            "bathroom", "toilet", "closet",
            "utility", "laundry", "balcony"
        )

        minimum = (
            700.0 if any(t in room_type for t in small_room_types)
            else self.min_dimension
        )

        if min(width, depth) < minimum:
            warnings.append(
                f"Room {room_id}: narrow bounding dimension "
                f"({width:.0f} x {depth:.0f} mm)."
            )

        if min(width, depth) > 0:
            ratio = max(width, depth) / min(width, depth)

            if ratio > self.max_aspect_ratio:
                warnings.append(
                    f"Room {room_id}: unusual aspect ratio "
                    f"({ratio:.2f}). Review room proportions."
                )

        # Check for orthogonal corners. Non-orthogonal geometry
        # is reported, not automatically changed.
        for i in range(n):
            prev = polygon[i - 1]
            current = polygon[i]
            nxt = polygon[(i + 1) % n]

            v1 = (prev[0] - current[0], prev[1] - current[1])
            v2 = (nxt[0] - current[0], nxt[1] - current[1])

            l1 = hypot(*v1)
            l2 = hypot(*v2)

            if l1 == 0 or l2 == 0:
                continue

            cosine = (
                v1[0] * v2[0] + v1[1] * v2[1]
            ) / (l1 * l2)

            # A right angle has cosine approximately zero.
            if abs(cosine) > 0.0524:
                warnings.append(
                    f"Room {room_id}: corner {i} is not approximately "
                    "90 degrees."
                )

        return {
            "errors": errors,
            "warnings": warnings,
            "area": area,
            "width": width,
            "depth": depth,
        }

    @staticmethod
    def segments_intersect(a, b, c, d):
        def orientation(p, q, r):
            value = (
                (q[0] - p[0]) * (r[1] - p[1])
                - (q[1] - p[1]) * (r[0] - p[0])
            )
            if abs(value) < 1e-7:
                return 0
            return 1 if value > 0 else -1

        def on_segment(p, q, r):
            return (
                min(p[0], r[0]) - 1e-7 <= q[0] <= max(p[0], r[0]) + 1e-7
                and min(p[1], r[1]) - 1e-7 <= q[1] <= max(p[1], r[1]) + 1e-7
            )

        o1 = orientation(a, b, c)
        o2 = orientation(a, b, d)
        o3 = orientation(c, d, a)
        o4 = orientation(c, d, b)

        if o1 != o2 and o3 != o4:
            return True

        return (
            (o1 == 0 and on_segment(a, c, b))
            or (o2 == 0 and on_segment(a, d, b))
            or (o3 == 0 and on_segment(c, a, d))
            or (o4 == 0 and on_segment(c, b, d))
        )

    def validate_wall_geometry(self, floor):
        walls = self.get(floor, "walls", []) or []

        errors = []
        warnings = []
        shared_candidates = []
        duplicate_candidates = []
        invalid_walls = []

        for i, wall in enumerate(walls):
            start = self.point(self.get(wall, "start"))
            end = self.point(self.get(wall, "end"))

            length = self.distance(start, end)
            height = float(self.get(wall, "height", 0))
            thickness = float(self.get(wall, "thickness", 0))

            if length <= 0.001 or height <= 0 or thickness <= 0:
                invalid_walls.append(
                    self.get(wall, "id", f"wall_{i}")
                )
                continue

            for other in walls[i + 1:]:
                other_start = self.point(
                    self.get(other, "start")
                )
                other_end = self.point(
                    self.get(other, "end")
                )

                if self.same_segment(
                    start, end, other_start, other_end
                ):
                    first_room = self.get(wall, "room_id")
                    second_room = self.get(other, "room_id")

                    if first_room != second_room:
                        shared_candidates.append({
                            "wall_a": self.get(wall, "id"),
                            "wall_b": self.get(other, "id"),
                            "room_a": first_room,
                            "room_b": second_room,
                        })
                    else:
                        duplicate_candidates.append({
                            "wall_a": self.get(wall, "id"),
                            "wall_b": self.get(other, "id"),
                        })

                elif self.near_endpoint(
                    start, end, other_start, other_end
                ):
                    warnings.append(
                        f"Possible wall endpoint misalignment: "
                        f"{self.get(wall, 'id')} and "
                        f"{self.get(other, 'id')}."
                    )

        if invalid_walls:
            errors.append(
                f"{len(invalid_walls)} walls have invalid dimensions."
            )

        if duplicate_candidates:
            warnings.append(
                f"{len(duplicate_candidates)} duplicate wall candidates found."
            )

        if shared_candidates:
            warnings.append(
                f"{len(shared_candidates)} shared wall pairs found. "
                "Review before merging physical wall meshes."
            )

        return {
            "errors": errors,
            "warnings": warnings,
            "invalid_walls": invalid_walls,
            "shared_wall_candidates": shared_candidates,
            "duplicate_wall_candidates": duplicate_candidates,
        }

    def same_segment(self, a, b, c, d):
        tolerance = self.snap_tolerance
        return (
            (
                self.distance(a, c) <= tolerance
                and self.distance(b, d) <= tolerance
            )
            or (
                self.distance(a, d) <= tolerance
                and self.distance(b, c) <= tolerance
            )
        )

    def near_endpoint(self, a, b, c, d):
        tolerance = self.snap_tolerance
        pairs = [
            (a, c), (a, d), (b, c), (b, d)
        ]
        return any(
            0.001 < self.distance(p, q) <= tolerance
            for p, q in pairs
        )

    def validate_floor(self, floor):
        rooms = self.get(floor, "rooms", []) or []

        room_reports = {}
        errors = []
        warnings = []

        for room in rooms:
            room_id = self.get(room, "id", "unknown")
            result = self.validate_room(room)
            room_reports[room_id] = result

            errors.extend(result["errors"])
            warnings.extend(result["warnings"])

        wall_report = self.validate_wall_geometry(floor)

        errors.extend(wall_report["errors"])
        warnings.extend(wall_report["warnings"])

        return {
            "valid": len(errors) == 0,
            "room_count": len(rooms),
            "wall_count": len(
                self.get(floor, "walls", []) or []
            ),
            "errors": errors,
            "warnings": warnings,
            "room_reports": room_reports,
            "wall_report": wall_report,
        }
