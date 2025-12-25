import httpx
import hashlib
from datetime import datetime, timedelta
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from config import settings
from db.models.user import User
from db.models.refresh_token import RefreshToken


REFRESH_TTL_DAYS = 30


def hash_refresh(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


async def auth_login(
    username: str,
    password: str,
    db: AsyncSession,
):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{settings.AUTH_SERVER_URL}/api/core/auth/login/",
            json={"username": username, "password": password},
            timeout=10,
        )

    if response.status_code != 200:
        raise ValueError("Invalid credentials")

    data = response.json()

    external_user_id = data["user_id"]
    refresh_token = data["refresh"]
    refresh_hash = hash_refresh(refresh_token)

    # 1️⃣ ищем или создаём пользователя
    result = await db.execute(
        select(User).where(User.external_user_id == external_user_id)
    )
    user = result.scalar_one_or_none()

    if not user:
        user = User(
            external_user_id=external_user_id,
            username=data["username"],
            full_name=data["full_name"],
        )
        db.add(user)
        await db.flush()  # получаем user.id

    # 2️⃣ сохраняем refresh
    db.add(
        RefreshToken(
            user_id=user.id,
            token_hash=refresh_hash,
            expires_at=datetime.utcnow() + timedelta(days=REFRESH_TTL_DAYS),
            is_revoked=False,
        )
    )

    await db.commit()

    return data


async def auth_refresh(
    refresh_token: str,
    db: AsyncSession,
):
    refresh_hash = hash_refresh(refresh_token)

    # 1️⃣ ищем refresh в БД
    result = await db.execute(
        select(RefreshToken)
        .where(RefreshToken.token_hash == refresh_hash)
        .where(RefreshToken.is_revoked == False)
    )
    stored_token = result.scalar_one_or_none()

    if not stored_token:
        raise ValueError("Invalid refresh token")

    if stored_token.expires_at < datetime.utcnow():
        raise ValueError("Refresh token expired")

    # 2️⃣ дёргаем внешний auth
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{settings.AUTH_SERVER_URL}/api/core/auth/refresh/",
            json={"refresh": refresh_token},
            timeout=10,
        )

    if response.status_code != 200:
        raise ValueError("Invalid refresh token")

    data = response.json()

    new_refresh = data["refresh"]
    new_refresh_hash = hash_refresh(new_refresh)

    # 3️⃣ инвалидируем старый refresh
    await db.execute(
        update(RefreshToken)
        .where(RefreshToken.id == stored_token.id)
        .values(is_revoked=True)
    )

    # 4️⃣ сохраняем новый
    db.add(
        RefreshToken(
            user_id=stored_token.user_id,
            token_hash=new_refresh_hash,
            expires_at=datetime.utcnow() + timedelta(days=REFRESH_TTL_DAYS),
            is_revoked=False,
        )
    )

    await db.commit()

    return data
