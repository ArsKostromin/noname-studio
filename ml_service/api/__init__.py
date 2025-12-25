"""
API роуты для ML сервиса
"""
from fastapi import APIRouter

from api.ml_routes import router as ml_router
from api.auth.router import router as auth_router

router = APIRouter()

router.include_router(ml_router, prefix="/ml", tags=["ml"])
router.include_router(auth_router)