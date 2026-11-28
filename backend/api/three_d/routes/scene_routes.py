import logging

from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from backend.db.models import User
from backend.api.three_d.services.scene_service import scene_service
from backend.api.three_d.routes import require_user


router = APIRouter(prefix="/api/3d", tags=["3D Scenes"])

logger = logging.getLogger(__name__)


class SceneRequest(BaseModel):
    layout: Dict[str, Any]
    metadata: Dict[str, Any] = Field(default_factory=dict)


@router.get("/health")
def three_d_health():
    return {
        "status": "success",
        "service": "Nesto 3D API",
        "message": "3D backend is running."
    }


@router.post("/generate")
def generate_3d_scene(
    data: SceneRequest,
    user: User = Depends(require_user),
):

    try:
        scene = scene_service.create_scene(
            layout=data.layout,
            user_id=user.user_id,
            metadata=data.metadata,
        )

        return {
            "status": "success",
            "scene_id": scene["id"],
            "scene": scene,
        }

    except (ValueError, TypeError) as error:
        raise HTTPException(
            status_code=422,
            detail=str(error),
        ) from error

    except Exception as error:
        logger.exception("3D scene generation failed.")

        raise HTTPException(
            status_code=500,
            detail="Unable to generate the 3D scene.",
        ) from error


@router.get("/scene/{scene_id}")
def get_3d_scene(
    scene_id: str,
    user: User = Depends(require_user),
):

    try:
        logger.info(
            "3D scene access: scene_id=%s, authenticated_user_id=%s",
            scene_id,
            user.user_id,
        )
        scene = scene_service.get_scene(
            scene_id,
            user.user_id,
        )

        return {
            "status": "success",
            "scene": scene,
        }

    except FileNotFoundError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error),
        ) from error

    except PermissionError as error:
        raise HTTPException(
            status_code=403,
            detail=str(error),
        ) from error

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error


@router.get("/layers/{scene_id}")
def get_3d_layers(
    scene_id: str,
    layer: Optional[str] = Query(default=None),
    user: User = Depends(require_user),
):

    try:
        result = scene_service.get_layers(
            scene_id,
            user.user_id,
            layer,
        )

        return {
            "status": "success",
            **result,
        }

    except FileNotFoundError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error),
        ) from error

    except PermissionError as error:
        raise HTTPException(
            status_code=403,
            detail=str(error),
        ) from error

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error
