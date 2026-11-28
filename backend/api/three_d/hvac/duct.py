"""HVAC duct geometry generator."""

from .hvac_models import DuctSegment, HVACSystem


class DuctGenerator:

    def generate(self, routes: list[dict]) -> HVACSystem:
        system = HVACSystem(system_id="hvac_duct_system")

        for index, route in enumerate(routes):
            start = route.get("start")
            end = route.get("end")

            if not start or not end or len(start) != 2 or len(end) != 2:
                raise ValueError(
                    f"Duct {index}: start and end must be [x, y]"
                )

            width = float(route.get("width", 200))
            height = float(route.get("height", 150))

            if width <= 0 or height <= 0:
                raise ValueError(f"Duct {index}: dimensions must be positive")

            system.ducts.append(
                DuctSegment(
                    duct_id=route.get("duct_id", f"duct_{index + 1}"),
                    start=start,
                    end=end,
                    elevation_start=float(route.get("elevation_start", 2700)),
                    elevation_end=float(route.get("elevation_end", 2700)),
                    width=width,
                    height=height,
                    material=route.get("material", "GI"),
                    connected_to=route.get("connected_to", []),
                )
            )

        return system
