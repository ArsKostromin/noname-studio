"""
Конфигурация ML сервиса
"""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Настройки приложения"""

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
    JWT_ALGORITHM: str = "HS256"

    # =========================
    # CORS
    # =========================
    CORS_ORIGINS: List[str] = [
        "http://localhost:8000",
        "http://localhost:3000",
    ]

    # =========================
    # ML
    # =========================
    MODEL_PATH: str = "models/"
    HF_API_KEY: str 

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
