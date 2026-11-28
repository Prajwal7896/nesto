"""Conservative axis-aligned bounding-box collision validation."""

import math


class CollisionValidator:

    REQUIRED = ("x", "y", "z", "width", "height", "depth")

    @staticmethod
    def _valid_number(value):
        return (
            isinstance(value, (int, float))
            and not isinstance(value, bool)
            and math.isfinite(value)
        )

    def _validate_box(self, obj):
        errors = []

        for key in self.REQUIRED:
            if key not in obj:
                errors.append(f"Missing bounding box field: {key}")
            elif not self._valid_number(obj[key]):
                errors.append(f"Invalid bounding box value: {key}")

        if errors:
            return errors

        for key in ("width", "height", "depth"):
            if obj[key] <= 0:
                errors.append(f"{key} must be positive")

        return errors

    def overlaps(self, first, second):
        for obj in (first, second):
            errors = self._validate_box(obj)
            if errors:
                raise ValueError(errors)

        return (
            first["x"] < second["x"] + second["width"]
            and first["x"] + first["width"] > second["x"]
            and first["y"] < second["y"] + second["height"]
            and first["y"] + first["height"] > second["y"]
            and first["z"] < second["z"] + second["depth"]
            and first["z"] + first["depth"] > second["z"]
        )

    def validate(self, objects):
        errors = []
        warnings = []

        if not isinstance(objects, list):
            return {
                "valid": False,
                "errors": ["Objects must be a list"],
                "warnings": []
            }

        for index, obj in enumerate(objects):
            if not isinstance(obj, dict):
                errors.append(f"Object {index} must be a dictionary")
                continue

            box_errors = self._validate_box(obj)

            for error in box_errors:
                errors.append(f"Object {index}: {error}")

        if errors:
            return {
                "valid": False,
                "errors": errors,
                "warnings": warnings
            }

        for i in range(len(objects)):
            for j in range(i + 1, len(objects)):
                if self.overlaps(objects[i], objects[j]):
                    warnings.append(
                        f"Objects {i} and {j} have overlapping bounding boxes"
                    )

        return {
            "valid": True,
            "errors": errors,
            "warnings": warnings
        }
