"""Drainage pipeline generator with slope calculations."""

from .plumbing_models import PipeSegment, PlumbingSystem


class DrainageGenerator:
    DEFAULT_DIAMETER = 75.0
    DEFAULT_SLOPE_PERCENT = 1.0

    def generate(self, routes: list[dict]) -> PlumbingSystem:
        system = PlumbingSystem(
            system_id="drainage_system",
            system_type="drainage",
        )

        for index, route in enumerate(routes):
            start = route.get("start")
            end = route.get("end")

            if not start or not end or len(start) != 2 or len(end) != 2:
                raise ValueError(f"Route {index}: start and end must be [x, y] coordinates")

            dx = end[0] - start[0]
            dy = end[1] - start[1]
            horizontal_length = (dx * dx + dy * dy) ** 0.5

            slope = float(route.get("slope_percent", self.DEFAULT_SLOPE_PERCENT))

            if horizontal_length <= 0:
                raise ValueError(f"Route {index}: horizontal length must be positive")

            if slope <= 0:
                raise ValueError(f"Route {index}: drainage slope must be positive")

            elevation_start = float(route.get("elevation_start", 0))
            drop = horizontal_length * slope / 100.0
            elevation_end = elevation_start - drop

            if route.get("elevation_end") is not None:
                elevation_end = float(route["elevation_end"])
                actual_slope = (
                    (elevation_start - elevation_end) / horizontal_length
                ) * 100.0
                if actual_slope <= 0:
                    raise ValueError(f"Route {index}: end elevation must be lower than start")
                slope = actual_slope

            system.pipes.append(
                PipeSegment(
                    pipe_id=route.get("pipe_id", f"drain_pipe_{index + 1}"),
                    system_type="drainage",
                    start=start,
                    end=end,
                    diameter=float(route.get("diameter", self.DEFAULT_DIAMETER)),
                    elevation_start=elevation_start,
                    elevation_end=elevation_end,
                    material=route.get("material", "PVC"),
                    slope_percent=slope,
                    flow_direction="start_to_end",
                    connected_to=route.get("connected_to", []),
                )
            )

        return system
