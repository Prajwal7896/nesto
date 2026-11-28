
import logging

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from backend.api.rag.pipeline import generate
from backend.db.models import User, get_db
from backend.memory.conversation import list_projects


router = APIRouter()
logger = logging.getLogger(__name__)


class PromptRequest(BaseModel):
    prompt: str = Field(min_length=1)
    customization: dict = Field(default_factory=dict)
    mode: str = "new"
    project_id: str | None = None


def get_current_user(request: Request, db: Session):
    user_id = request.session.get("user_id")

    if not user_id:
        raise HTTPException(
            status_code=401,
            detail="Please log in to generate a floor plan."
        )

    user = db.query(User).filter(
        User.user_id == user_id
    ).first()

    if not user:
        request.session.clear()
        raise HTTPException(
            status_code=401,
            detail="User session expired. Please log in again."
        )

    return user


@router.get("/projects")
async def get_projects(
    request: Request,
    db: Session = Depends(get_db)
):
    user = get_current_user(request, db)

    return {
        "status": "success",
        "projects": list_projects(user.user_id)
    }


@router.post("/generate")
async def generate_floor_plan(
    data: PromptRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    user = get_current_user(request, db)

    prompt = data.prompt.strip()

    if not prompt:
        raise HTTPException(
            status_code=400,
            detail="Please provide a valid house plan prompt."
        )

    if data.mode not in {"new", "modify"}:
        raise HTTPException(
            status_code=400,
            detail="Invalid design mode."
        )

    if data.mode == "modify" and not data.project_id:
        raise HTTPException(
            status_code=400,
            detail="Select a project to modify."
        )

    try:
        result = generate(
            prompt=prompt,
            user_id=user.user_id,
            customization=data.customization,
            mode=data.mode,
            project_id=data.project_id,
        )

        if not isinstance(result, dict):
            raise HTTPException(
                status_code=500,
                detail="Invalid generation response."
            )

        if result.get("status") != "success":
            return {
                "status": "error",
                "message": result.get(
                    "reason",
                    result.get(
                        "message",
                        result.get("error", "Floor plan generation failed.")
                    )
                ),
                "stage": result.get("stage"),
                "details": result.get("details"),
                "timings": result.get("timings", {}),
            }

        layout = result.get("layout")

        if not isinstance(layout, dict):
            raise HTTPException(
                status_code=500,
                detail="Generated layout is missing."
            )

        validation = result.get("validation") or {}
        files = result.get("files") or {}
        rooms = layout.get("rooms") or []

        return {
            "status": "success",
            "project_id": result.get("project_id"),
            "project_name": result.get("project_name"),
            "mode": result.get("mode"),
            "layout": layout,
            "validation": validation,
            "files": files,
            "timings": result.get("timings", {}),
            "summary": {
                "rooms": layout.get("room_count", len(rooms)),
                "valid": validation.get("valid", False),
            },
        }

    except HTTPException:
        raise

    except Exception:
        logger.exception("Floor plan generation endpoint failed.")

        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred during generation."
        )
