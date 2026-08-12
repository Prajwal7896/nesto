from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.api.rag.pipeline import generate
from backend.db.models import User, get_db

router = APIRouter()


class PromptRequest(BaseModel):
    prompt: str


@router.post("/generate")
async def generate_floor_plan(
    data: PromptRequest,
    db: Session = Depends(get_db),
):
    user = db.query(User).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No user found",
        )

    result = generate(data.prompt, user.user_id)

    if result.get("status") != "success":
        return result

    layout = result.get("layout", {})
    validation = result.get("validation", {})

    return {
        "status": "success",
        "layout": layout,
        "validation": validation,
        "files": result.get("files", {}),
        "summary": {
            "rooms": len(layout.get("rooms", [])),
            "valid": validation.get("valid", False),
        },
    }