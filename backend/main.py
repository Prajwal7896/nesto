
import os
from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from backend.api.auth import router as auth_router
from backend.api.generate import router as generate_router

# Three.js 3D backend routers
from backend.api.three_d.routes.scene_routes import router as three_d_scene_router
from backend.api.three_d.routes.construction_routes import router as three_d_construction_router
from backend.api.three_d.routes.export_routes import router as three_d_export_router

from backend.db.models import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Nesto Construction Portal")

app.add_middleware(
    SessionMiddleware,
    secret_key=os.environ["SESSION_SECRET"],
    same_site="lax",
    https_only=os.getenv("ENVIRONMENT") == "production",
)

app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/output", StaticFiles(directory="output"), name="output")

# Existing routes — preserved
app.include_router(auth_router)
app.include_router(generate_router)

# New Three.js 3D routes
app.include_router(three_d_scene_router)
app.include_router(three_d_construction_router)
app.include_router(three_d_export_router)
