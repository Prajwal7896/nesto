"""Basic geometry structure validation."""

import math


class GeometryValidator:

    @staticmethod
    def _valid_number(value):
        return (
            isinstance(value, (int, float))
            and not isinstance(value, bool)
            and math.isfinite(value)
        )

    def validate(self, geometry):
        errors = []
        warnings = []

        if not isinstance(geometry, dict):
            return {
                "valid": False,
                "errors": ["Geometry must be a dictionary"],
                "warnings": []
            }

        vertices = geometry.get("vertices")
        faces = geometry.get("faces")

        if vertices is None:
            if not any(key in geometry for key in ("position", "dimensions")):
                errors.append("Geometry needs vertices or position/dimensions")
            return {
                "valid": not errors,
                "errors": errors,
                "warnings": warnings
            }

        if not isinstance(vertices, list) or len(vertices) < 3:
            errors.append("Geometry must contain at least three vertices")
        else:
            for index, vertex in enumerate(vertices):
                if not isinstance(vertex, (list, tuple)) or len(vertex) != 3:
                    errors.append(f"Vertex {index} must contain x, y and z")
                    continue

                if not all(self._valid_number(v) for v in vertex):
                    errors.append(f"Vertex {index} contains invalid coordinates")

        if faces is not None:
            if not isinstance(faces, list):
                errors.append("Faces must be a list")
            else:
                for face_index, face in enumerate(faces):
                    if not isinstance(face, (list, tuple)) or len(face) < 3:
                        errors.append(f"Face {face_index} is invalid")
                        continue

                    for vertex_index in face:
                        if (
                            not isinstance(vertex_index, int)
                            or isinstance(vertex_index, bool)
                            or vertex_index < 0
                            or vertex_index >= len(vertices)
                        ):
                            errors.append(
                                f"Face {face_index} contains an invalid vertex index"
                            )
                            break

        if faces == []:
            warnings.append("Geometry has no faces")

        return {
            "valid": not errors,
            "errors": errors,
            "warnings": warnings
        }
