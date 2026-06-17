from typing import Literal

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from starlette import status

from app.models import UserORM


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get(self, user_id: int) -> UserORM | None:
        return self.db.get(UserORM, user_id)

    def get_by_email(self, email: str) -> UserORM | None:
        query = select(UserORM).where(UserORM.email == email)
        return self.db.execute(query).scalar_one_or_none()

    def create(self, email: str, hashed_password: str, full_name: str | None) -> UserORM:
        user = UserORM(email=email,
                       hashed_password=hashed_password,
                       full_name=full_name)
        try:
            self.db.add(user)
            self.db.flush()
            self.db.refresh(user)

            return user
        except SQLAlchemyError:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def set_role(self, user: UserORM, role: Literal["user", "editor", "admin"]) -> UserORM:
        user.role = role
        self.db.add(user)
        self.db.flush()
        self.db.refresh(user)
        return user
