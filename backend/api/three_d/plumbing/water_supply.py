"""Cold-water supply pipeline generator."""

from .plumbing_models import PipeSegment, PlumbingSystem


class WaterSupplyGenerator:
    DEFAULT_DIAMETER = 20.0

    def generate(self, routes: list[dict]) -> PlumbingSystem:
        system = PlumbingSystem(
            system_id="cold_water_system",
            system_type="cold_water",
        )

        for index, route in enumerate(routes):
            start = route.get("start")
            end = route.get("end")

            if not start or not end or len(start) != 2 or len(end) != 2:
                raise ValueError(f"Route {index}: start and end must be [x, y] coordinates")

            pipe = PipeSegment(
                pipe_id=route.get("pipe_id", f"cold_pipe_{index + 1}"),
                system_type="cold_water",
                start=start,
                end=end,
                diameter=float(route.get("diameter", self.DEFAULT_DIAMETER)),
                elevation_start=float(route.get("elevation_start", 0)),
                elevation_end=float(route.get("elevation_end", 0)),
                material=route.get("material", "CPVC"),
                connected_to=route.get("connected_to", []),
            )

            system.pipes.append(pipe)

        return system
