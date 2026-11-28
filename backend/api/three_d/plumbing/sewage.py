"""Sewage and soil-waste pipeline generator."""

from .plumbing_models import PipeSegment, PlumbingSystem


class SewageGenerator:
    DEFAULT_DIAMETERS = {
        "soil": 110.0,
        "waste": 75.0,
        "vent": 50.0,
    }

    def generate(self, routes: list[dict]) -> PlumbingSystem:
        system = PlumbingSystem(
            system_id="sewage_system",
            system_type="sewage",
        )

        for index, route in enumerate(routes):
            start = route.get("start")
            end = route.get("end")

            if not start or not end or len(start) != 2 or len(end) != 2:
                raise ValueError(f"Route {index}: start and end must be [x, y] coordinates")

            pipe_type = route.get("pipe_type", "soil").lower()

            if pipe_type not in self.DEFAULT_DIAMETERS:
                raise ValueError(f"Unsupported sewage pipe type: {pipe_type}")

            dx = end[0] - start[0]
            dy = end[1] - start[1]
            horizontal_length = (dx * dx + dy * dy) ** 0.5

            elevation_start = float(route.get("elevation_start", 0))
            slope = float(route.get("slope_percent", 1.0 if pipe_type != "vent" else 0.0))

            if pipe_type != "vent" and (horizontal_length <= 0 or slope <= 0):
                raise ValueError(f"Route {index}: soil/waste pipe requires positive length and slope")

            calculated_end = elevation_start - horizontal_length * slope / 100.0

            elevation_end = float(route.get("elevation_end", calculated_end))

            system.pipes.append(
                PipeSegment(
                    pipe_id=route.get("pipe_id", f"sewage_pipe_{index + 1}"),
                    system_type=f"sewage_{pipe_type}",
                    start=start,
                    end=end,
                    diameter=float(
                        route.get("diameter", self.DEFAULT_DIAMETERS[pipe_type])
                    ),
                    elevation_start=elevation_start,
                    elevation_end=elevation_end,
                    material=route.get("material", "PVC"),
                    slope_percent=slope,
                    flow_direction=route.get("flow_direction", "start_to_end"),
                    connected_to=route.get("connected_to", []),
                )
            )

        return system
