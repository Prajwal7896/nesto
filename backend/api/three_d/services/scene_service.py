import json
import re
from pathlib import Path
from typing import Any, Dict, Optional

from backend.api.three_d.core.scene_builder import SceneBuilder


SCENE_DIRECTORY = Path("output") / "three_d" / "scenes"

SCENE_ID_PATTERN = re.compile(r"^[A-Za-z0-9_-]{1,80}$")


class SceneService:

    def __init__(self):
        self.builder = SceneBuilder()
        SCENE_DIRECTORY.mkdir(parents=True, exist_ok=True)

    def _scene_path(self, scene_id: str) -> Path:
        if not SCENE_ID_PATTERN.fullmatch(scene_id):
            raise ValueError("Invalid scene ID.")

        return SCENE_DIRECTORY / f"{scene_id}.json"

    def create_scene(
        self,
        layout: Dict[str, Any],
        user_id: Any,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:

        scene_metadata = {
            "source": "Nesto 2D planner",
            "owner_user_id": str(user_id),
        }

        if metadata:
            scene_metadata.update(metadata)

        scene_metadata["owner_user_id"] = str(user_id)

        scene = self.builder.build_dict(
            layout,
            metadata=scene_metadata,
        )

        path = self._scene_path(scene["id"])

        with path.open("w", encoding="utf-8") as file:
            json.dump(
                scene,
                file,
                indent=2,
                ensure_ascii=False,
                allow_nan=False,
            )

        return scene

    def get_scene(
        self,
        scene_id: str,
        user_id: Any,
    ) -> Dict[str, Any]:

        path = self._scene_path(scene_id)

        if not path.exists():
            raise FileNotFoundError("3D scene not found.")

        with path.open("r", encoding="utf-8") as file:
            scene = json.load(file)

        owner_id = scene.get("metadata", {}).get("owner_user_id")

        if str(owner_id) != str(user_id):
            raise PermissionError("You do not have access to this scene.")

        return scene

    def get_layers(
        self,
        scene_id: str,
        user_id: Any,
        layer: Optional[str] = None,
    ) -> Dict[str, Any]:

        scene = self.get_scene(scene_id, user_id)

        allowed_layers = {
            "rooms",
            "walls",
            "doors",
            "windows",
            "site_features",
            "open_spaces",
            "structure",
            "engineering",
        }

        if layer and layer not in allowed_layers:
            raise ValueError(
                f"Unsupported layer. Choose from {sorted(allowed_layers)}"
            )

        floors = []

        for floor in scene.get("floors", []):
            floor_data = {"id": floor["id"]}

            selected = allowed_layers if layer is None else {layer}

            for key in selected:
                floor_data[key] = floor.get(key, {} if key in {
                    "structure", "engineering"
                } else [])

            floors.append(floor_data)

        return {
            "scene_id": scene["id"],
            "layers": sorted(selected),
            "floors": floors,
        }


scene_service = SceneService()

