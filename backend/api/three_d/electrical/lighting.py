"""Lighting fixture generator."""

from .electrical_models import ElectricalComponent


class LightingGenerator:

    def generate(self, lights: list[dict]) -> list[ElectricalComponent]:
        result = []

        for index, light in enumerate(lights):
            position = light.get("position", [0, 0])

            if len(position) != 2:
                raise ValueError(f"Light {index}: position must be [x, y]")

            result.append(
                ElectricalComponent(
                    component_id=light.get(
                        "component_id", f"light_{index + 1}"
                    ),
                    component_type="lighting",
                    position=position,
                    elevation=float(light.get("elevation", 2700)),
                    room_id=light.get("room_id"),
                    properties={
                        "light_type": light.get("light_type", "LED"),
                        "wattage": float(light.get("wattage", 12)),
                        "color_temperature": int(
                            light.get("color_temperature", 4000)
                        ),
                        "lumens": float(light.get("lumens", 1000)),
                        "mounting": light.get("mounting", "ceiling"),
                    },
                )
            )

        return result
