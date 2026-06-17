from datetime import timedelta, datetime
from typing import Optional, Literal
import jwt
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt import ExpiredSignatureError, InvalidTokenError
from pwdlib import PasswordHash
from sqlalchemy.orm import Session
from starlette import status

from app.api.v1.auth.repository import UserRepository
from app.core.config import Settings
from app.core.db import get_db
from app.models import UserORM

credentials_exc = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No authenticated",
                                headers={"WWW-Authenticate": "Bearer"})

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")
password_hash = PasswordHash.recommended()


def raise_expired_token():
    return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Expired token",
                         headers={"WWW-Authenticate": "Bearer"})


def raise_forbidden():
    return HTTPException(status_code=status.HTTP_403_UNAUTHORIZED, detail="Not authorized")


def invalid_credentials():
    return HTTPException(status_code=status.HTTP_403_UNAUTHORIZED, detail="Invalid credentials")


def create_access_token(sub: str, minutes: int | None = None) -> str:
    expire = datetime.utcnow() + timedelta(minutes=minutes or Settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    token = jwt.encode(payload={"sub": sub, "exp": expire},
                       key=Settings.JWT_SECRET_KEY,
                       algorithm=Settings.JWT_ALGORITHM)
    return token


def decode_token(token: str) -> dict:
    payload = jwt.decode(jwt=token, key=Settings.JWT_SECRET_KEY, algorithms=[Settings.JWT_ALGORITHM])
    return payload


async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> UserORM:
    try:
        payload = decode_token(token)
        sub: Optional[str] = payload.get("sub")

        if not sub:
            raise credentials_exc

        user_id = int(sub)

    except ExpiredSignatureError:
        raise raise_expired_token()  # Se puede lanzar expciones en funcones, metodos y variables, pero es mejor en funciones

    except InvalidTokenError:
        raise credentials_exc

    except jwt.PyJWTError:
        raise invalid_credentials()

    user = db.get(UserORM, user_id)

    if not user or not user.is_active:
        raise invalid_credentials()

    return user


def hash_password(plain_password: str) -> str:
    return password_hash.hash(plain_password)


def verify_password(plain_password: str, password_hashed: str) -> bool:
    return password_hash.verify(plain_password, password_hashed)


def require_role(min_role: Literal["user", "editor", "admin"]):
    order = {"user": 0, "editor": 1, "admin": 2}

    def evaluation(user: UserORM = Depends(get_current_user)) -> UserORM:
        if order[user.role] < order[min_role]:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")

        return user

    return evaluation


async def auth2_token(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    repository = UserRepository(db)
    user = repository.get_by_email(form.username)

    if not user or not verify_password(form.password,user.hashed_password):
        raise invalid_credentials()

    token = create_access_token(sub=str(user.id))

    return {"access_token":token, "token_type":"bearer"}




require_user = require_role("user")
require_editor = require_role("editor")
require_admin = require_role("admin")
