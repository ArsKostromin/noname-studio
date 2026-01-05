import httpx
from config import settings


async def auth_login(username: str, password: str):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{settings.AUTH_SERVER_URL}/api/core/auth/login/",
            json={
                "username": username,
                "password": password,
            },
            timeout=10,
        )

    if response.status_code != 200:
        raise ValueError("Invalid credentials")

    return response.json()


async def auth_refresh(refresh_token: str):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{settings.AUTH_SERVER_URL}/api/core/auth/refresh/",
            json={"refresh": refresh_token},
            timeout=10,
        )

    if response.status_code != 200:
        raise ValueError("Invalid refresh token")

    return response.json()
