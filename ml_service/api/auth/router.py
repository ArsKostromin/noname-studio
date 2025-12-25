from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api.auth.schemas import (
    LoginRequest,
    LoginResponse,
    RefreshRequest,
    RefreshResponse,
)
from api.auth.service import auth_login, auth_refresh
from db.session import AsyncSessionLocal


router = APIRouter(prefix="/api/core/auth", tags=["auth"])


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


@router.post("/login/", response_model=LoginResponse)
async def login(
    payload: LoginRequest,
    db: AsyncSession = Depends(get_db),
):
    try:
        return await auth_login(payload.username, payload.password, db)
    except ValueError:
        raise HTTPException(status_code=401, detail="Неверный логин или пароль")


@router.post("/refresh/", response_model=RefreshResponse)
async def refresh(
    payload: RefreshRequest,
    db: AsyncSession = Depends(get_db),
):
    try:
        return await auth_refresh(payload.refresh, db)
    except ValueError:
        raise HTTPException(
            status_code=401,
            detail="Невалидный или истёкший refresh токен",
        )
