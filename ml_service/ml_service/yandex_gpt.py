# ml_service/services/yandex_gpt.py
import httpx
from typing import Optional
from ml_service.config import settings


class YandexGPTClient:
    """
    Клиент для общения с YandexGPT API
    """

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.ai.yandex.net/v1/"  # пример, уточни для своего тарифа
        self.headers = {
            "Authorization": f"Api-Key {self.api_key}",
            "Content-Type": "application/json",
        }

    async def ask(self, prompt: str, max_tokens: int = 500, temperature: float = 0.3) -> str:
        """
        Отправляем запрос в YandexGPT и возвращаем текст ответа
        """
        url = f"{self.base_url}engines/text-bison-001/completions"
        payload = {
            "prompt": prompt,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }

        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(url, headers=self.headers, json=payload)
            resp.raise_for_status()
            data = resp.json()
            # структура ответа может отличаться, пример:
            # data["completions"][0]["text"]
            try:
                return data["completions"][0]["text"]
            except (KeyError, IndexError):
                return "Ошибка при генерации ответа от YandexGPT"

# === Пример использования ===
# from services.yandex_gpt import YandexGPTClient
# gpt_client = YandexGPTClient(api_key="ВАШ_API_KEY")
# answer = await gpt_client.ask("Привет, расскажи про производные")
