"""Electrical wire route generator."""

from .electrical_models import WireSegment, ElectricalSystem


class WiringGenerator:

    def generate(self, routes: list[dict]) -> ElectricalSystem:
        system = ElectricalSystem(system_id="electrical_wiring")

        for index, route in enumerate(routes):
            start = route.get("start")
            end = route.get("end")

            if not start or not end or len(start) != 2 or len(end) != 2:
                raise ValueError(
                    f"Route {index}: start and end must be [x, y] coordinates"
                )

            wire = WireSegment(
                wire_id=route.get("wire_id", f"wire_{index + 1}"),
                start=start,
                end=end,
                elevation_start=float(route.get("elevation_start", 0)),
                elevation_end=float(route.get("elevation_end", 0)),
                wire_type=route.get("wire_type", "copper"),
                circuit_id=route.get("circuit_id", "circuit_1"),
                voltage=float(route.get("voltage", 230)),
                current_rating=route.get("current_rating"),
                connected_to=route.get("connected_to", []),
            )

            system.wires.append(wire)

        return system
