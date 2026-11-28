"""Air-conditioning unit generator."""

from .hvac_models import HVACComponent


class AirConditioningGenerator:

    def generate(self, units: list[dict]) -> list[HVACComponent]:
        result = []

        for index, unit in enumerate(units):
            position = unit.get("position", [0, 0])

            if len(position) != 2:
                raise ValueError(f"AC unit {index}: position must be [x, y]")

            result.append(
                HVACComponent(
                    component_id=unit.get("component_id", f"ac_unit_{index + 1}"),
                    component_type="air_conditioner",
                    position=position,
                    elevation=float(unit.get("elevation", 2200)),
                    room_id=unit.get("room_id"),
                    properties={
                        "unit_type": unit.get("unit_type", "split"),
                        "capacity_ton": float(unit.get("capacity_ton", 1.5)),
                        "brand": unit.get("brand"),
                        "orientation": unit.get("orientation", "north"),
                        "outdoor_unit_position": unit.get("outdoor_unit_position"),
                        "power_watts": float(unit.get("power_watts", 0)),
                    },
                )
            )

        return result
