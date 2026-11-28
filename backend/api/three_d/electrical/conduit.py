"""Electrical conduit route generator."""

from .electrical_models import ConduitSegment, ElectricalSystem


class ConduitGenerator:

    def generate(self, routes: list[dict]) -> ElectricalSystem:
        system = ElectricalSystem(system_id="electrical_conduits")

        for index, route in enumerate(routes):
            start = route.get("start")
            end = route.get("end")

            if not start or not end or len(start) != 2 or len(end) != 2:
                raise ValueError(
                    f"Route {index}: start and end must be [x, y] coordinates"
                )

            diameter = float(route.get("diameter", 20))

            if diameter <= 0:
                raise ValueError(f"Route {index}: conduit diameter must be positive")

            conduit = ConduitSegment(
                conduit_id=route.get("conduit_id", f"conduit_{index + 1}"),
                start=start,
                end=end,
                diameter=diameter,
                elevation_start=float(route.get("elevation_start", 0)),
                elevation_end=float(route.get("elevation_end", 0)),
                material=route.get("material", "PVC"),
                connected_to=route.get("connected_to", []),
            )

            system.conduits.append(conduit)

        return system
