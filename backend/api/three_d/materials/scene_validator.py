"""Complete scene validation."""

from .geometry_validator import GeometryValidator
from .dimension_validator import DimensionValidator
from .collision_validator import CollisionValidator
from .material_models import Material


class SceneValidator:

    def __init__(self):
        self.geometry_validator = GeometryValidator()
        self.dimension_validator = DimensionValidator()
        self.collision_validator = CollisionValidator()

    def validate(self, scene):
        errors = []
        warnings = []

        if not isinstance(scene, dict):
            return {
                "valid": False,
                "errors": ["Scene must be a dictionary"],
                "warnings": []
            }

        objects = scene.get("objects", [])

        if not isinstance(objects, list):
            return {
                "valid": False,
                "errors": ["Scene objects must be a list"],
                "warnings": []
            }

        collision_objects = []

        for index, obj in enumerate(objects):
            if not isinstance(obj, dict):
                errors.append(f"Object {index} must be a dictionary")
                continue

            prefix = f"Object {index}"

            geometry = obj.get("geometry")
            if geometry is not None:
                result = self.geometry_validator.validate(geometry)
                errors.extend(
                    f"{prefix}: {error}" for error in result["errors"]
                )
                warnings.extend(
                    f"{prefix}: {warning}" for warning in result["warnings"]
                )

            dimensions = obj.get("dimensions")
            if dimensions is not None:
                result = self.dimension_validator.validate(dimensions)
                errors.extend(
                    f"{prefix}: {error}" for error in result["errors"]
                )
                warnings.extend(
                    f"{prefix}: {warning}" for warning in result["warnings"]
                )

            material = obj.get("material")
            if isinstance(material, dict):
                try:
                    material_obj = Material(
                        name=material.get("name", ""),
                        category=material.get("category", "general"),
                        color=material.get("color", "#FFFFFF"),
                        roughness=material.get("roughness", 0.7),
                        metalness=material.get("metalness", 0.0),
                        opacity=material.get("opacity", 1.0),
                        transparent=material.get("transparent", False),
                        texture_path=material.get("texture_path"),
                        normal_map_path=material.get("normal_map_path"),
                        repeat_x=material.get("repeat_x", 1.0),
                        repeat_y=material.get("repeat_y", 1.0)
                    )
                    result = material_obj.validate()
                    errors.extend(
                        f"{prefix}: {error}" for error in result["errors"]
                    )
                except (TypeError, ValueError) as exc:
                    errors.append(f"{prefix}: Invalid material: {exc}")

            box = obj.get("bounding_box")
            if box is not None:
                if isinstance(box, dict):
                    collision_objects.append(box)
                else:
                    errors.append(f"{prefix}: bounding_box must be a dictionary")

        collision_result = self.collision_validator.validate(collision_objects)
        errors.extend(collision_result["errors"])
        warnings.extend(collision_result["warnings"])

        return {
            "valid": not errors,
            "errors": errors,
            "warnings": warnings,
            "object_count": len(objects)
        }
