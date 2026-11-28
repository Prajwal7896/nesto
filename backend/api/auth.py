from fastapi import APIRouter, Request, Form, Depends, status , UploadFile, File

from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

import os
import shutil
from backend.db.models import User, get_db

router = APIRouter()

templates = Jinja2Templates(directory="frontend")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
def get_logged_in_user(request: Request, db: Session):
    user_id = request.session.get("user_id")

    if not user_id:
        return None

    user = db.query(User).filter(
        User.user_id == user_id
    ).first()

    if not user:
        request.session.clear()

    return user

@router.get("/", response_class=HTMLResponse)
async def home(request: Request, db: Session = Depends(get_db)):
    user_id = request.session.get("user_id")

    user = None
    if user_id:
        user = db.query(User).filter(User.user_id == user_id).first()

    if not user:
        return RedirectResponse(url="/login", status_code=303)

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"user": user}
    )


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="login.html"
    )


@router.post("/login")
async def login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.email == email).first()

    if user is None or not pwd_context.verify(
        password,
        user.password_hash,
    ):
        return templates.TemplateResponse(
            request=request,
            name="login.html",
            context={"error": "Invalid email or password"},
            status_code=401,
        )

    request.session.clear()
    request.session["user_id"] = user.user_id

    return RedirectResponse(
        url="/profile",
        status_code=303,
    )



@router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="register.html"
    )


@router.post("/register")
async def register(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...),
    role: str = Form(...),
    terms: str = Form(...),
    db: Session = Depends(get_db)
):
    if password != confirm_password:
        return templates.TemplateResponse(
            request,
            "register.html",
            {
                "error": "Passwords do not match"
            }
        )

    existing_user = db.query(User).filter(User.email == email).first()

    if existing_user:
        return templates.TemplateResponse(
            request,
            "register.html",
            {
                "error": "Email already exists"
            }
        )

    hashed_password = pwd_context.hash(password)

    new_user = User(
        name=name,
        email=email,
        password_hash=hashed_password
    )

    db.add(new_user)
    db.commit()

    return RedirectResponse(
        url="/login",
        status_code=status.HTTP_302_FOUND
    )


@router.get("/profile", response_class=HTMLResponse)
async def profile(
    request: Request,
    db: Session = Depends(get_db)
):
    user = get_logged_in_user(request, db)

    if not user:
        return RedirectResponse(
            url="/login",
            status_code=303
        )

    return templates.TemplateResponse(
        request=request,
        name="profile.html",
        context={"user": user}
    )



@router.post("/logout")
async def logout(request: Request):
    request.session.clear()

    return RedirectResponse(
        url="/login",
        status_code=303,
    )


@router.get("/reset-password", response_class=HTMLResponse)
async def reset_password_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="reset_password.html"
    )

@router.post("/reset-password")
async def reset_password():
    return {
        "message": "Password reset functionality to be implemented"
    }

@router.post("/profile/update")
async def update_profile(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    phone_number: str = Form(None),
    age: int = Form(None),
    role: str = Form(None),
    profile_image: UploadFile = File(None),
    db: Session = Depends(get_db)
):
    user_id = request.session.get("user_id")

    if not user_id:
        return RedirectResponse(url="/login", status_code=303)

    user = db.query(User).filter(User.user_id == user_id).first()

    if not user:
        request.session.clear()
        return RedirectResponse(url="/login", status_code=303)

    # Check whether another user already owns this email
    existing_user = db.query(User).filter(
        User.email == email,
        User.user_id != user.user_id
    ).first()

    if existing_user:
        return templates.TemplateResponse(
            request=request,
            name="profile.html",
            context={
                "user": user,
                "error": "This email is already registered with another account."
            },
            status_code=400
        )

    user.name = name
    user.email = email
    user.phone_number = phone_number
    user.age = age
    user.role = role

    if profile_image and profile_image.filename:
        os.makedirs("static/uploads", exist_ok=True)

        filename = os.path.basename(profile_image.filename)
        filepath = os.path.join("static/uploads", filename)

        with open(filepath, "wb") as buffer:
            shutil.copyfileobj(profile_image.file, buffer)

        user.image_url = f"/static/uploads/{filename}"

    try:
        db.commit()
    except IntegrityError:
        db.rollback()

        return templates.TemplateResponse(
            request=request,
            name="profile.html",
            context={
                "user": user,
                "error": "This email is already registered."
            },
            status_code=400
        )

    return RedirectResponse(url="/", status_code=303)