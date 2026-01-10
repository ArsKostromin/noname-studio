"""
FastAPI сервис для ML функционала
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
import os
import sys

# Добавляем текущую директорию в путь для импортов
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Настройка логирования
os.makedirs("logs", exist_ok=True)
logger.add("logs/ml_service.log", rotation="10 MB", retention="7 days", level="INFO")

from config import settings
from api import router

app = FastAPI(
    title="URFU ML Service",
    description="ML сервис для анализа данных студентов",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключаем роуты
app.include_router(router, prefix="")


@app.get("/")
async def root():
    """Health check endpoint"""
    return {"status": "ok", "service": "ml_service"}


@app.get("/health")
async def health():
    """Health check с детальной информацией"""
    return {
        "status": "healthy",
        "service": "ml_service",
        "version": "1.0.0"
    }

