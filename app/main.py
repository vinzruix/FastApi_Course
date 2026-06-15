from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, status, Depends
from app.core.db import Base, engine
from app.api.v1.posts.router import router as post_router
from app.api.v1.auth.router import router as auth_router

load_dotenv()


def create_app() -> FastAPI:
    app = FastAPI(
        title="Mini Blog"
    )
    Base.metadata.create_all(bind=engine)  # Esto es por ahora, para lo real se usan migraciones
    app.include_router(auth_router, prefix="/api/v1")
    app.include_router(post_router, prefix="/api/v1")

    return app

app = create_app()
