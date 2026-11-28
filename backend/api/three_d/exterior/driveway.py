"""Driveway geometry generator."""


class DrivewayGenerator:

    def generate(self, driveways: list[dict]) -> list[dict]:
        result = []

        for index, driveway in enumerate(driveways):
            points = driveway.get("points", [])

            if len(points) < 2:
                raise ValueError(
                    f"Driveway {index}: at least two [x, y] points are required"
                )

            if any(not isinstance(point, (list, tuple)) or len(point) != 2
                   for point in points):
                raise ValueError(f"Driveway {index}: every point must be [x, y]")

            width = float(driveway.get("width", 3000))

            if width <= 0:
                raise ValueError(f"Driveway {index}: width must be positive")

            segments = []
            total_length = 0.0

            for point_index in range(len(points) - 1):
                start = points[point_index]
                end = points[point_index + 1]

                length = (
                    (end[0] - start[0]) ** 2 +
                    (end[1] - start[1]) ** 2
                ) ** 0.5

                segments.append({
                    "start": start,
                    "end": end,
                    "length": length,
                })

                total_length += length

            result.append({
                "driveway_id": driveway.get(
                    "driveway_id", f"driveway_{index + 1}"
                ),
                "points": points,
                "segments": segments,
                "total_length": total_length,
                "width": width,
                "surface": driveway.get("surface", "concrete"),
                "color": driveway.get("color", "#777777"),
            })

        return result
