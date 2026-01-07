"""
API роуты для ML сервиса
"""
from fastapi import APIRouter

from .auth.router import router as auth_router
from .ai.router import router as ml_router  

router = APIRouter()

# Auth роуты
router.include_router(
    auth_router,
    tags=["Auth"]
)

# AI / ML роуты
router.include_router(
    ml_router,
    prefix="/ml",
    tags=["ML"]
)
