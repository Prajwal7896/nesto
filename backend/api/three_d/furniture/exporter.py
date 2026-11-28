from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class FurnitureExporter:
    """Exports furniture specifications to JSON."""

    def export_dict(
        self,
        furniture_items: list[dict[str, Any]],
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        return {
            "schema_version": "1.0",
            "type": "nesto_furniture_scene",
            "unit": "mm",
            "metadata": metadata or {},
            "furniture_count": len(furniture_items),
            "furniture": furniture_items,
        }

    def export_json(
        self,
        furniture_items: list[dict[str, Any]],
        output_path: str | Path,
        metadata: dict[str, Any] | None = None,
    ) -> str:
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        data = self.export_dict(furniture_items, metadata)

        with path.open("w", encoding="utf-8") as file:
            json.dump(data, file, indent=2, ensure_ascii=False)

        return str(path.resolve())
