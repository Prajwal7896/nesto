from fastapi import APIRouter, Depends, HTTPException, Query

from backend.db.models import User
from backend.api.three_d.services.scene_service import scene_service
from backend.api.three_d.services.construction_service import (
    construction_service,
)
from backend.api.three_d.routes import require_user


router = APIRouter(prefix="/api/3d", tags=["3D Construction"])


@router.get("/construction/{scene_id}")
def get_construction_sequence(
    scene_id: str,
    user: User = Depends(require_user),
):

    try:
        scene = scene_service.get_scene(
            scene_id,
            user.user_id,
        )

        return {
            "status": "success",
            **construction_service.get_construction(scene),
        }

    except FileNotFoundError as error:
        raise HTTPException(404, str(error)) from error

    except PermissionError as error:
        raise HTTPException(403, str(error)) from error

    except ValueError as error:
        raise HTTPException(422, str(error)) from error


@router.get("/progress/{scene_id}")
def get_construction_progress(
    scene_id: str,
    timestamp: float = Query(default=0.0, ge=0.0),
    user: User = Depends(require_user),
):

    try:
        scene = scene_service.get_scene(
            scene_id,
            user.user_id,
        )

        return {
            "status": "success",
            **construction_service.get_progress(
                scene,
                timestamp,
            ),
        }

    except FileNotFoundError as error:
        raise HTTPException(404, str(error)) from error

    except PermissionError as error:
        raise HTTPException(403, str(error)) from error

    except ValueError as error:
        raise HTTPException(422, str(error)) from error
