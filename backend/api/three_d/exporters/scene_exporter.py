"""Unified scene exporter for Nesto 3D."""

from pathlib import Path

from .json_exporter import JSONExporter
from .gltf_exporter import GLTFExporter
from .glb_exporter import GLBExporter


class SceneExporter:

    SUPPORTED_FORMATS = ("json", "gltf", "glb")

    def __init__(self, units="mm"):
        self.json_exporter = JSONExporter()
        self.gltf_exporter = GLTFExporter(units=units)
        self.glb_exporter = GLBExporter(units=units)

    def export(self, scene, output_path, format=None):
        path = Path(output_path)

        selected_format = (
            format.lower() if format
            else path.suffix.lstrip(".").lower()
        )

        if selected_format not in self.SUPPORTED_FORMATS:
            raise ValueError(
                f"Unsupported format: {selected_format}. "
                f"Choose from {self.SUPPORTED_FORMATS}"
            )

        if path.suffix.lower() != f".{selected_format}":
            path = path.with_suffix(f".{selected_format}")

        if selected_format == "json":
            return self.json_exporter.export(scene, path)

        if selected_format == "gltf":
            return self.gltf_exporter.export(scene, path)

        if selected_format == "glb":
            return self.glb_exporter.export(scene, path)

        raise ValueError("Export failed: unsupported format")
