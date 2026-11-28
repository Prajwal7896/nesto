"""Compound wall geometry generator."""


class CompoundWallGenerator:

    def generate(self, walls: list[dict]) -> list[dict]:
        result = []

        for index, wall in enumerate(walls):
            start = wall.get("start")
            end = wall.get("end")

            if not start or not end or len(start) != 2 or len(end) != 2:
                raise ValueError(f"Wall {index}: start and end must be [x, y]")

            length = (
                (end[0] - start[0]) ** 2 +
                (end[1] - start[1]) ** 2
            ) ** 0.5

            height = float(wall.get("height", 1800))
            thickness = float(wall.get("thickness", 150))

            if length <= 0 or height <= 0 or thickness <= 0:
                raise ValueError(f"Wall {index}: dimensions must be positive")

            result.append({
                "wall_id": wall.get("wall_id", f"compound_wall_{index + 1}"),
                "start": start,
                "end": end,
                "length": length,
                "height": height,
                "thickness": thickness,
                "material": wall.get("material", "concrete"),
                "base_elevation": float(wall.get("base_elevation", 0)),
                "color": wall.get("color", "#B8B8B8"),
            })

        return result
