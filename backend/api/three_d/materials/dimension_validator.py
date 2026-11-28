"""Dimension and unit validation. Backend dimensions use millimetres."""

import math


class DimensionValidator:

    DIMENSION_KEYS = ("width", "height", "depth", "length", "thickness")

    @staticmethod
    def _valid_number(value):
        return (
            isinstance(value, (int, float))
            and not isinstance(value, bool)
            and math.isfinite(value)
        )

    def validate(self, dimensions):
        errors = []
        warnings = []

        if not isinstance(dimensions, dict):
            return {
                "valid": False,
                "errors": ["Dimensions must be a dictionary"],
                "warnings": []
            }

        found = False

        for key in self.DIMENSION_KEYS:
            if key not in dimensions:
                continue

            found = True
            value = dimensions[key]

            if not self._valid_number(value):
                errors.append(f"{key} must be a finite number")
            elif value <= 0:
                errors.append(f"{key} must be greater than zero")

        if not found:
            errors.append("No supported dimensions were supplied")

        unit = dimensions.get("unit", "mm")

        if unit != "mm":
            errors.append("Backend dimensions must use millimetres (mm)")

        return {
            "valid": not errors,
            "errors": errors,
            "warnings": warnings
        }

    def to_metres(self, dimensions):
        result = self.validate(dimensions)

        if not result["valid"]:
            raise ValueError(result["errors"])

        return {
            key: value / 1000.0
            for key, value in dimensions.items()
            if key in self.DIMENSION_KEYS
        }
