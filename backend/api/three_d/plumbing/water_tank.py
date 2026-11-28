"""Water tank specification and capacity generator."""

from .plumbing_models import WaterTank


class WaterTankGenerator:

    def generate(self, tanks: list[dict]) -> list[WaterTank]:
        result = []

        for index, data in enumerate(tanks):
            position = data.get("position", [0, 0])

            if len(position) != 2:
                raise ValueError(f"Tank {index}: position must be [x, y]")

            width = float(data["width"])
            depth = float(data["depth"])
            height = float(data["height"])

            if min(width, depth, height) <= 0:
                raise ValueError(f"Tank {index}: dimensions must be positive")

            tank = WaterTank(
                tank_id=data.get("tank_id", f"water_tank_{index + 1}"),
                position=position,
                width=width,
                depth=depth,
                height=height,
                tank_type=data.get("tank_type", "overhead"),
                material=data.get("material", "plastic"),
            )

            result.append(tank)

        return result

    @staticmethod
    def calculate_capacity(width: float, depth: float, height: float) -> float:
        if min(width, depth, height) <= 0:
            raise ValueError("Tank dimensions must be positive")

        return width * depth * height / 1_000_000
