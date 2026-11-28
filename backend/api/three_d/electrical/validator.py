"""Electrical system specification validator."""


class ElectricalValidator:

    def validate_wire(self, wire) -> list[str]:
        errors = []

        if wire.length() <= 0:
            errors.append(f"{wire.wire_id}: wire length must be positive")

        if wire.voltage <= 0:
            errors.append(f"{wire.wire_id}: voltage must be positive")

        if wire.current_rating is not None and wire.current_rating <= 0:
            errors.append(f"{wire.wire_id}: current rating must be positive")

        return errors

    def validate_system(self, system) -> dict:
        errors = []
        warnings = []

        ids = []

        for component in system.components:
            ids.append(component.component_id)

            if len(component.position) != 2:
                errors.append(
                    f"{component.component_id}: position must be [x, y]"
                )

        for wire in system.wires:
            ids.append(wire.wire_id)
            errors.extend(self.validate_wire(wire))

        for conduit in system.conduits:
            ids.append(conduit.conduit_id)

            if conduit.diameter <= 0:
                errors.append(
                    f"{conduit.conduit_id}: conduit diameter must be positive"
                )

            if len(conduit.start) != 2 or len(conduit.end) != 2:
                errors.append(
                    f"{conduit.conduit_id}: coordinates must be [x, y]"
                )

        if len(ids) != len(set(ids)):
            errors.append("Duplicate electrical component IDs found")

        if not system.wires:
            warnings.append("No wire routes supplied")

        if not system.components:
            warnings.append("No electrical components supplied")

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
        }
