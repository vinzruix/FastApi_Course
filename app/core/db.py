import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session, DeclarativeBase

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./blog.db")

engine_kwargs = {}

if DATABASE_URL.startswith("sqlite"):
    engine_kwargs["connect_args"] = {"check_same_thread": False}

engine = create_engine(DATABASE_URL, echo=True, future=True,
                       **engine_kwargs)  # Future significa usar la version nueva de sqlalchemy
session_local = sessionmaker(bind=engine, autoflush=False,
                             class_=Session)  # AutoFlush, hace que no se hagan los cambios hasta hacer el commit


class Base(DeclarativeBase):
    pass


def get_db():
    db = session_local()
    try:
        yield db
    finally:
        db.close()
