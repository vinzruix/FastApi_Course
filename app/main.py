from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, status, Depends
from app.core.db import Base, engine
from app.api.v1.posts.router import router as post_router

load_dotenv()


def create_app() -> FastAPI:
    app = FastAPI(
        title="Mini Blog"
    )
    Base.metadata.create_all(bind=engine)  # Esto es por ahora, para lo real se usan migraciones
    app.include_router(post_router)

    return app

app = create_app()
