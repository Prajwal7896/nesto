from fastapi import Depends, HTTPException, Request
from sqlalchemy.orm import Session

from backend.db.models import User, get_db


def require_user(
    request: Request,
    db: Session = Depends(get_db),
) -> User:

    user_id = request.session.get("user_id")

    if not user_id:
        raise HTTPException(
            status_code=401,
            detail="Please log in to access your 3D house."
        )

    user = db.query(User).filter(
        User.user_id == user_id
    ).first()

    if not user:
        request.session.clear()

        raise HTTPException(
            status_code=401,
            detail="Your session has expired. Please log in again."
        )

    return user
