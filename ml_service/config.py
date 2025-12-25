"""
Конфигурация ML сервиса
"""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    DB_HOST: str = "db"
    DB_NAME: str = "urfu_db"
    DB_USER: str = "urfu_user"
    DB_PASSWORD: str = "urfu_password"
    DB_PORT: int = 5432

    AUTH_SERVER_URL: str = "http://django:8000"
    JWT_PUBLIC_KEY: str = "PUBLIC_KEY_FROM_AUTH"
    JWT_ALGORITHM: str = "HS256"

    CORS_ORIGINS: List[str] = [
        "http://localhost:8000",
        "http://localhost:3000",
    ]

    MODEL_PATH: str = "models/"

    @property
    def DATABASE_URL(self) -> str:
        return (
            f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
