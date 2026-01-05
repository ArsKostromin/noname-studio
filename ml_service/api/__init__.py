"""
API роуты для ML сервиса
"""
from fastapi import APIRouter

from .ml_routes import router as ml_router
from .auth.router import router as auth_router

router = APIRouter()

# Auth роуты (логин / refresh)
router.include_router(
    auth_router,
    tags=["Auth"]
)

# ML роуты
router.include_router(
    ml_router,
    prefix="/ml",
    tags=["ML"]
)
