from pathlib import Path
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from backend.db.models import User
from backend.api.three_d.services.scene_service import scene_service
from backend.api.three_d.exporters.scene_exporter import SceneExporter
from backend.api.three_d.routes import require_user


router = APIRouter(prefix="/api/3d", tags=["3D Export"])

EXPORT_DIRECTORY = Path("output") / "three_d" / "exports"


class ExportRequest(BaseModel):
    format: Literal["json", "gltf", "glb"] = "glb"


@router.post("/export/{scene_id}")
def export_3d_scene(
    scene_id: str,
    data: ExportRequest,
    user: User = Depends(require_user),
):

    try:
        scene = scene_service.get_scene(
            scene_id,
            user.user_id,
        )

        EXPORT_DIRECTORY.mkdir(
            parents=True,
            exist_ok=True,
        )

        filename = f"{scene_id}.{data.format}"
        output_path = EXPORT_DIRECTORY / filename

        exporter = SceneExporter(units="mm")

        result = exporter.export(
            scene,
            output_path,
            format=data.format,
        )

        return {
            "status": "success",
            "scene_id": scene_id,
            "format": data.format,
            "filename": filename,
            "file_url": f"/output/three_d/exports/{filename}",
            "size_bytes": output_path.stat().st_size,
            "export_details": result,
            "warning": (
                "This scene currently contains architectural scene data. "
                "GLB mesh geometry requires the mesh-generation stage."
                if data.format in ("gltf", "glb")
                else None
            ),
        }

    except FileNotFoundError as error:
        raise HTTPException(404, str(error)) from error

    except PermissionError as error:
        raise HTTPException(403, str(error)) from error

    except ValueError as error:
        raise HTTPException(422, str(error)) from error

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail="3D scene export failed.",
        ) from error
