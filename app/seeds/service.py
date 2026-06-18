from contextlib import contextmanager
from typing import Optional
from fastapi import Depends
from pwdlib import PasswordHash
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.core.db import get_db, session_local
from app.models import UserORM, CategoryORM, TagORM
from .data.categories import CATEGORIES
from .data.tags import TAGS
from .data.users import USERS


def hash_password(plain: str):
    return PasswordHash.recommended().hash(plain)


@contextmanager
def atomic(db: Session):
    try:
        yield
        db.commit()
    except Exception:
        db.rollback()
        raise


def _user_by_email(email: str, db: Session = Depends(get_db)) -> Optional[UserORM]:
    return db.execute(select(UserORM).where(UserORM.email == email)).scalars().first()


def _category_by_slug(slug: str, db: Session = Depends(get_db)) -> Optional[CategoryORM]:
    return db.execute(select(CategoryORM).where(CategoryORM.slug == slug)).scalars().first()


def _tag_by_name(name: str, db: Session = Depends(get_db)) -> Optional[TagORM]:
    return db.execute(select(TagORM).where(TagORM.name == name)).scalars().first()


def seed_users(db: Session) -> None:
    with atomic(db):
        for data in USERS:
            obj = _user_by_email(data["email"], db)
            if obj:
                changed=False
                if obj.full_name != data.get("full_name"):
                    obj.full_name = data.get("full_name")
                    changed = True

                if data.get("password"):
                    obj.hashed_password = hash_password(data.get("password"))
                    changed = True

                if data.get("role"):
                    obj.role_enum = data.get("role")
                    changed = True

                if changed:
                    db.add(obj)

            else:
                db.add(UserORM(email=data["email"],
                               full_name=data["full_name"],
                               role=data["role"],
                               hashed_password=hash_password(data["password"])))


def seed_categories(db : Session) -> None:
    with atomic(db):
        for data in CATEGORIES:
            obj = _category_by_slug(data["slug"], db)

            if obj:
                if obj.name != data.get("name"):
                    obj.full_name = data.get("name")
                    db.add(obj)

            else:
                db.add(CategoryORM(name=data["name"],slug=data["slug"]))

def seed_tags(db: Session) -> None:
    with atomic(db):
        for data in TAGS:
            obj = _tag_by_name(db=db, name=data["name"])
            if obj:
                if obj.name != data["name"]:
                    obj.name = data["name"]
                    db.add(obj)
            else:
                db.add(TagORM(name=data["name"]))

def run_all() -> None:
    with session_local() as db:
        seed_users(db)
        seed_categories(db)
        seed_tags(db)




def run_users() -> None:
    with session_local() as db:
        seed_users(db)


def run_categories() -> None:
    with session_local() as db:
        seed_categories(db)


def run_tags() -> None:
    with session_local() as db:
        seed_tags(db)








