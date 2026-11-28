"""JSON scene exporter for Nesto 3D."""

import json
from dataclasses import asdict, is_dataclass
from pathlib import Path


class JSONExporter:

    @staticmethod
    def _serialize(value):
        if is_dataclass(value):
            return asdict(value)

        if hasattr(value, "to_dict") and callable(value.to_dict):
            return value.to_dict()

        raise TypeError(
            f"Object of type {type(value).__name__} is not JSON serializable"
        )

    def export(self, scene, output_path):
        if not isinstance(scene, dict):
            raise TypeError("Scene must be a dictionary")

        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        content = json.dumps(
            scene,
            indent=2,
            default=self._serialize,
            allow_nan=False
        )

        path.write_text(content, encoding="utf-8")

        return {
            "success": True,
            "format": "json",
            "path": str(path),
            "size_bytes": path.stat().st_size
        }

    def to_json(self, scene):
        if not isinstance(scene, dict):
            raise TypeError("Scene must be a dictionary")

        return json.dumps(
            scene,
            indent=2,
            default=self._serialize,
            allow_nan=False
        )
