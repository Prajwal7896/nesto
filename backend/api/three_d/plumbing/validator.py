"""Validation utilities for plumbing specifications."""

from typing import Iterable


class PlumbingValidator:

    def validate_pipe(self, pipe) -> list[str]:
        errors = []

        if pipe.diameter <= 0:
            errors.append(f"{pipe.pipe_id}: diameter must be positive")

        if len(pipe.start) != 2 or len(pipe.end) != 2:
            errors.append(f"{pipe.pipe_id}: coordinates must contain [x, y]")

        if pipe.length() <= 0:
            errors.append(f"{pipe.pipe_id}: pipe length must be positive")

        if pipe.system_type in {"drainage", "sewage_soil", "sewage_waste"}:
            if pipe.slope_percent <= 0:
                errors.append(f"{pipe.pipe_id}: drainage slope must be positive")

            if pipe.elevation_end >= pipe.elevation_start:
                errors.append(f"{pipe.pipe_id}: gravity pipe must descend toward its end")

        return errors

    def validate_system(self, system) -> dict:
        errors = []
        warnings = []

        pipe_ids = [pipe.pipe_id for pipe in system.pipes]

        if len(pipe_ids) != len(set(pipe_ids)):
            errors.append("Duplicate pipe IDs found")

        known_ids = set(pipe_ids)
        known_ids.update(f.fixture_id for f in system.fixtures)

        for pipe in system.pipes:
            errors.extend(self.validate_pipe(pipe))

            for connection in pipe.connected_to:
                if connection not in known_ids:
                    warnings.append(
                        f"{pipe.pipe_id}: connection '{connection}' is not present in this system"
                    )

        for fixture in system.fixtures:
            if len(fixture.position) != 2:
                errors.append(f"{fixture.fixture_id}: position must be [x, y]")

            for connection in fixture.connections:
                if connection not in known_ids:
                    warnings.append(
                        f"{fixture.fixture_id}: connection '{connection}' is not present"
                    )

        for tank in system.tanks:
            if min(tank.width, tank.depth, tank.height) <= 0:
                errors.append(f"{tank.tank_id}: invalid tank dimensions")

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
        }

    def validate_multiple(self, systems: Iterable) -> dict:
        results = {}

        for system in systems:
            results[system.system_id] = self.validate_system(system)

        return {
            "valid": all(item["valid"] for item in results.values()),
            "systems": results,
        }
