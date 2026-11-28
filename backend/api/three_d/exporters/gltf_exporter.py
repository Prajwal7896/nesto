"""glTF 2.0 exporter for Nesto 3D."""

import base64
import json
import math
import struct
from pathlib import Path


class GLTFExporter:

    def __init__(self, units="mm"):
        if units not in ("mm", "m"):
            raise ValueError("Units must be mm or m")

        self.units = units
        self.scale = 0.001 if units == "mm" else 1.0

    @staticmethod
    def _validate_vertices(vertices):
        if not isinstance(vertices, list) or len(vertices) < 3:
            raise ValueError("Mesh needs at least three vertices")

        result = []

        for vertex in vertices:
            if not isinstance(vertex, (list, tuple)) or len(vertex) != 3:
                raise ValueError("Every vertex must contain three coordinates")

            converted = []

            for value in vertex:
                if (
                    not isinstance(value, (int, float))
                    or isinstance(value, bool)
                    or not math.isfinite(value)
                ):
                    raise ValueError("Vertex coordinates must be finite numbers")

                converted.append(float(value))

            result.append(converted)

        return result

    @staticmethod
    def _triangulate(faces, vertex_count):
        if not isinstance(faces, list) or not faces:
            raise ValueError("Mesh must contain faces")

        indices = []

        for face in faces:
            if not isinstance(face, (list, tuple)) or len(face) < 3:
                raise ValueError("Every face must have at least three indices")

            for index in face:
                if (
                    not isinstance(index, int)
                    or isinstance(index, bool)
                    or index < 0
                    or index >= vertex_count
                ):
                    raise ValueError("Face contains an invalid vertex index")

            # Convert polygon faces into triangles using a fan.
            for i in range(1, len(face) - 1):
                indices.extend([face[0], face[i], face[i + 1]])

        return indices

    @staticmethod
    def _material(material):
        if not isinstance(material, dict):
            material = {}

        color = material.get("color", "#FFFFFF")

        if (
            not isinstance(color, str)
            or len(color) != 7
            or not color.startswith("#")
        ):
            color = "#FFFFFF"

        try:
            rgba = [
                int(color[1:3], 16) / 255.0,
                int(color[3:5], 16) / 255.0,
                int(color[5:7], 16) / 255.0,
                float(material.get("opacity", 1.0))
            ]
        except (ValueError, TypeError):
            rgba = [1.0, 1.0, 1.0, 1.0]

        rgba[3] = max(0.0, min(1.0, rgba[3]))

        roughness = float(material.get("roughness", 0.7))
        metalness = float(material.get("metalness", 0.0))

        return {
            "name": material.get("name", "DefaultMaterial"),
            "pbrMetallicRoughness": {
                "baseColorFactor": rgba,
                "metallicFactor": max(0.0, min(1.0, metalness)),
                "roughnessFactor": max(0.0, min(1.0, roughness))
            },
            "alphaMode": (
                "BLEND" if rgba[3] < 1.0 else "OPAQUE"
            ),
            "doubleSided": True
        }

    def build_document(self, scene):
        if not isinstance(scene, dict):
            raise TypeError("Scene must be a dictionary")

        objects = scene.get("objects", [])

        if not isinstance(objects, list):
            raise ValueError("Scene objects must be a list")

        binary = bytearray()
        buffer_views = []
        accessors = []
        meshes = []
        nodes = []
        materials = []
        material_lookup = {}

        def add_buffer(data, target):
            # glTF buffer views must be aligned to four bytes.
            while len(binary) % 4:
                binary.append(0)

            offset = len(binary)
            binary.extend(data)

            view_index = len(buffer_views)

            buffer_views.append({
                "buffer": 0,
                "byteOffset": offset,
                "byteLength": len(data),
                "target": target
            })

            return view_index

        for object_index, obj in enumerate(objects):
            if not isinstance(obj, dict):
                raise ValueError(f"Object {object_index} must be a dictionary")

            geometry = obj.get("geometry")

            if not isinstance(geometry, dict):
                continue

            vertices = self._validate_vertices(
                geometry.get("vertices")
            )

            indices = self._triangulate(
                geometry.get("faces"),
                len(vertices)
            )

            scaled_vertices = [
                [
                    x * self.scale,
                    y * self.scale,
                    z * self.scale
                ]
                for x, y, z in vertices
            ]

            flat_positions = [
                coordinate
                for vertex in scaled_vertices
                for coordinate in vertex
            ]

            position_data = struct.pack(
                "<" + "f" * len(flat_positions),
                *flat_positions
            )

            index_data = struct.pack(
                "<" + "I" * len(indices),
                *indices
            )

            position_view = add_buffer(position_data, 34962)
            index_view = add_buffer(index_data, 34963)

            minimum = [
                min(vertex[i] for vertex in scaled_vertices)
                for i in range(3)
            ]

            maximum = [
                max(vertex[i] for vertex in scaled_vertices)
                for i in range(3)
            ]

            position_accessor = len(accessors)

            accessors.append({
                "bufferView": position_view,
                "byteOffset": 0,
                "componentType": 5126,
                "count": len(vertices),
                "type": "VEC3",
                "min": minimum,
                "max": maximum
            })

            index_accessor = len(accessors)

            accessors.append({
                "bufferView": index_view,
                "byteOffset": 0,
                "componentType": 5125,
                "count": len(indices),
                "type": "SCALAR",
                "min": [min(indices)],
                "max": [max(indices)]
            })

            material_data = self._material(obj.get("material", {}))

            material_key = json.dumps(material_data, sort_keys=True)

            if material_key not in material_lookup:
                material_lookup[material_key] = len(materials)
                materials.append(material_data)

            material_index = material_lookup[material_key]

            mesh_index = len(meshes)

            meshes.append({
                "name": obj.get("name", f"Mesh_{object_index}"),
                "primitives": [{
                    "attributes": {
                        "POSITION": position_accessor
                    },
                    "indices": index_accessor,
                    "material": material_index,
                    "mode": 4
                }]
            })

            nodes.append({
                "name": obj.get("name", f"Object_{object_index}"),
                "mesh": mesh_index
            })

        document = {
            "asset": {
                "version": "2.0",
                "generator": "Nesto 3D Exporter"
            },
            "scene": 0,
            "scenes": [{
                "nodes": list(range(len(nodes)))
            }],
            "nodes": nodes,
            "meshes": meshes,
            "materials": materials,
            "accessors": accessors,
            "bufferViews": buffer_views,
            "buffers": [{
                "byteLength": len(binary)
            }]
        }

        return document, bytes(binary)

    def export(self, scene, output_path):
        document, binary = self.build_document(scene)

        document["buffers"][0]["uri"] = (
            "data:application/octet-stream;base64,"
            + base64.b64encode(binary).decode("ascii")
        )

        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        path.write_text(
            json.dumps(document, indent=2, allow_nan=False),
            encoding="utf-8"
        )

        return {
            "success": True,
            "format": "gltf",
            "path": str(path),
            "size_bytes": path.stat().st_size,
            "mesh_count": len(document["meshes"])
        }
