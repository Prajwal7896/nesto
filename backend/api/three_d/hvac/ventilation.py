"""Ventilation component generator."""

from .hvac_models import HVACComponent


class VentilationGenerator:

    def generate(self, vents: list[dict]) -> list[HVACComponent]:
        result = []

        for index, vent in enumerate(vents):
            position = vent.get("position", [0, 0])

            if len(position) != 2:
                raise ValueError(f"Vent {index}: position must be [x, y]")

            result.append(
                HVACComponent(
                    component_id=vent.get("component_id", f"vent_{index + 1}"),
                    component_type="ventilation",
                    position=position,
                    elevation=float(vent.get("elevation", 2700)),
                    room_id=vent.get("room_id"),
                    properties={
                        "vent_type": vent.get("vent_type", "exhaust"),
                        "airflow_cfm": float(vent.get("airflow_cfm", 0)),
                        "orientation": vent.get("orientation", "north"),
                        "mounting": vent.get("mounting", "ceiling"),
                    },
                )
            )

        return result
