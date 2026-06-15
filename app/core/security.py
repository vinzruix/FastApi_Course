from datetime import timedelta, datetime
from typing import Optional
import jwt
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
import os
from jwt import ExpiredSignatureError, InvalidTokenError
from starlette import status

SECRET_KEY = os.getenv("SECRET_KEY", "CHANGE-ME-IN-PROD")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

credentials_exc = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No authenticated",
                                headers={"WWW-Authenticate": "Bearer"})

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def raise_expired_token():
    return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Expired token",
                  headers={"WWW-Authenticate": "Bearer"})

def raise_forbidden():
    return HTTPException(status_code=status.HTTP_403_UNAUTHORIZED, detail="Not authorized")


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()  # Datos a codificar
    expire = datetime.utcnow() + (
                expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))  # Tiempo de expiracion
    to_encode.update({"exp": expire})
    token = jwt.encode(payload=to_encode, key=SECRET_KEY,
                       algorithm=ALGORITHM)  # payload es la info, key secret la firma
    return token


def decode_token(token: str) -> dict:
    payload = jwt.decode(jwt=token, key=SECRET_KEY, algorithms=[ALGORITHM])
    return payload


async def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    try:
        payload = decode_token(token)
        sub: Optional[str] = payload.get("sub")
        username: Optional[str] = payload.get("username")

        if not sub or not username:
            raise credentials_exc

        return {"email": sub, "username": username}

    except ExpiredSignatureError:
        raise raise_expired_token() # Se puede lanzar expciones en funcones, metodos y variables, pero es mejor en funciones

    except InvalidTokenError:
        raise credentials_exc
