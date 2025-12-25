"""
API роуты для ML сервиса
"""
from fastapi import APIRouter
from .ml_routes import router as ml_router

router = APIRouter()

router.include_router(ml_router, prefix="/ml", tags=["ML"])
