"""Binary glTF (GLB) exporter for Nesto 3D."""

import json
import struct
from pathlib import Path

from .gltf_exporter import GLTFExporter


class GLBExporter:

    MAGIC = 0x46546C67
    VERSION = 2
    JSON_CHUNK = 0x4E4F534A
    BIN_CHUNK = 0x004E4942

    def __init__(self, units="mm"):
        self.gltf_exporter = GLTFExporter(units=units)

    def export(self, scene, output_path):
        document, binary = self.gltf_exporter.build_document(scene)

        # GLB JSON chunks must be padded to four-byte alignment.
        json_data = json.dumps(
            document,
            separators=(",", ":"),
            allow_nan=False
        ).encode("utf-8")

        json_data += b" " * ((4 - len(json_data) % 4) % 4)

        binary += b"\x00" * ((4 - len(binary) % 4) % 4)

        document["buffers"][0]["byteLength"] = len(binary)

        # Re-encode after setting the final binary buffer length.
        json_data = json.dumps(
            document,
            separators=(",", ":"),
            allow_nan=False
        ).encode("utf-8")

        json_data += b" " * ((4 - len(json_data) % 4) % 4)

        json_chunk = (
            struct.pack("<I", len(json_data))
            + struct.pack("<I", self.JSON_CHUNK)
            + json_data
        )

        binary_chunk = (
            struct.pack("<I", len(binary))
            + struct.pack("<I", self.BIN_CHUNK)
            + binary
        )

        total_length = (
            12 + len(json_chunk) + len(binary_chunk)
        )

        glb_data = (
            struct.pack(
                "<III",
                self.MAGIC,
                self.VERSION,
                total_length
            )
            + json_chunk
            + binary_chunk
        )

        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(glb_data)

        return {
            "success": True,
            "format": "glb",
            "path": str(path),
            "size_bytes": path.stat().st_size,
            "mesh_count": len(document["meshes"])
        }
