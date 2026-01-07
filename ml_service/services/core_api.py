import httpx
from typing import List, Dict, Any
from config import settings


class CoreAPIClient:
    def __init__(self, access_token: str):
        self.base_url = settings.AUTH_SERVER_URL.rstrip("/")
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }

    async def get_my_schedule(self) -> List[Dict[str, Any]]:
        url = f"{self.base_url}/api/schedule/my-schedule/"
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, headers=self.headers)
            resp.raise_for_status()
            return resp.json()

    async def get_my_grades(self) -> List[Dict[str, Any]]:
        url = f"{self.base_url}/api/grades/my-grades/"
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, headers=self.headers)
            resp.raise_for_status()
            return resp.json()
