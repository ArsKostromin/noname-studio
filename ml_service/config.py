"""
Конфигурация ML сервиса
"""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # =========================
    # БАЗА ДАННЫХ
    # =========================
    DB_HOST: str
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str
    DB_PORT: int = 5432

    @property
    def DATABASE_URL(self) -> str:
        return (
            f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    # =========================
    # АВТОРИЗАЦИЯ
    # =========================
    AUTH_SERVER_URL: str = "http://django:8000"
    JWT_PUBLIC_KEY: str = "PUBLIC_KEY_FROM_AUTH"
    JWT_SECRET_KEY: str = "django-insecure-rh!+beoqrde_haod&xhod)jbjxx7jh$o2m!lhg(1h1kbxi!(my"
    JWT_ALGORITHM: str = "HS256"

    # =========================
    # CORS — ДЛЯ РАЗРАБОТКИ БЕЗ БОЛИ
    # =========================
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "http://155.212.144.126",
        "http://155.212.144.126:3000",
    ]

    # =========================
    # ML
    # =========================
    MODEL_PATH: str = "models/"
    HF_API_KEY: str = ""

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
