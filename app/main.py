from dotenv import load_dotenv
from fastapi import FastAPI
from app.core.db import Base, engine
from app.api.v1.posts.router import router as post_router
from app.api.v1.auth.router import router as auth_router
from app.api.v1.tags.router import router as tag_router
from app.api.v1.uploads.router import router as upload_router
from app.api.v1.categories.router import router as category_router

from fastapi.staticfiles import StaticFiles
import os

from app.core.middleware import register_middleware

load_dotenv()

MEDIA_DIR = "./media" # DIR CON LAS IMAGNES


def create_app() -> FastAPI:
    app = FastAPI(
        title="Mini Blog",
        swagger_ui_parameters={"persistAuthorization":True}
    )
    Base.metadata.create_all(bind=engine)  # Esto es por ahora, para lo real se usan migraciones
    register_middleware(app)
    app.include_router(auth_router, prefix="/api/v1")
    app.include_router(post_router, prefix="/api/v1")
    app.include_router(upload_router, prefix="/api/v1")
    app.include_router(tag_router, prefix="/api/v1")
    app.include_router(category_router, prefix="/api/v1")


    os.makedirs(MEDIA_DIR,exist_ok=True) # Crea la carpeta sino existe

    app.mount("/media", StaticFiles(directory=MEDIA_DIR),name="media") # Monta una ruta donde en base a una carpeta permite entrar a imagenes

    return app

app = create_app()
