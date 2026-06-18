import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session, DeclarativeBase

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./blog.db")

engine_kwargs = {}

if DATABASE_URL.startswith("sqlite"):
    engine_kwargs["connect_args"] = {"check_same_thread": False}

raw_url = os.environ["DATABASE_URL"]

url = raw_url

if url.startswith("postgres://"):
    url = "postgresql+psycopg://" + url[len("postgres://")]

elif url.startswith("postgresql://") and "+psycopg" not in url:
    url = "postgresql+psycopg://" + url[len("postgresql://")]


engine = create_engine(url, pool_pre_ping=True)

#engine = create_engine(DATABASE_URL, echo=False, future=True,
#                       **engine_kwargs)  # Future significa usar la version nueva de sqlalchemy



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
