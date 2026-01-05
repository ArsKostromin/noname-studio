from fastapi import APIRouter, HTTPException

from api.auth.schemas import (
    LoginRequest,
    LoginResponse,
    RefreshRequest,
    RefreshResponse,
)
from api.auth.service import auth_login, auth_refresh


router = APIRouter(prefix="/api/core/auth", tags=["auth"])


@router.post("/login/", response_model=LoginResponse)
async def login(payload: LoginRequest):
    try:
        return await auth_login(payload.username, payload.password)
    except ValueError:
        raise HTTPException(status_code=401, detail="Неверный логин или пароль")


@router.post("/refresh/", response_model=RefreshResponse)
async def refresh(payload: RefreshRequest):
    try:
        return await auth_refresh(payload.refresh)
    except ValueError:
        raise HTTPException(
            status_code=401,
            detail="Невалидный или истёкший refresh токен",
        )
