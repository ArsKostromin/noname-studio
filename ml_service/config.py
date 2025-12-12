"""
Конфигурация ML сервиса
"""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Настройки приложения"""
    
    # База данных
    DB_HOST: str = "db"
    DB_NAME: str = "urfu_db"
    DB_USER: str = "urfu_user"
    DB_PASSWORD: str = "urfu_password"
    DB_PORT: int = 5432
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:8000", "http://localhost:3000"]
    
    # ML настройки
    MODEL_PATH: str = "models/"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

