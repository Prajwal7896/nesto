from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from backend.api.auth import router as auth_router
from backend.api.generate import router as generate_router
from backend.db.models import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/output", StaticFiles(directory="output"), name="output")

app.include_router(auth_router)
app.include_router(generate_router)