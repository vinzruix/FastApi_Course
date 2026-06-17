import os


class Settings:
    JWT_SECRET_KEY : str = os.getenv("SECRET_KEY", "CHANGE-ME-IN-PROD")
    JWT_ALGORITHM : str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES : int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
