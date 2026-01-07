# ml_service/hf_gpt.py
import httpx
from config import settings

HF_API_URL = "https://api-inference.huggingface.co/models/"

class HFClient:
    def __init__(self, api_key: str, model: str="mistral‑medium"):
        self.api_key = api_key
        self.model = model
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        self.url = HF_API_URL + model

    async def ask(self, prompt: str, max_length: int = 256) -> str:
        """
        Отправляем prompt в HF API и получаем ответ
        """
        payload = {
            "inputs": prompt,
            "parameters": {"max_new_tokens": max_length}
        }

        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(self.url, headers=self.headers, json=payload)
            resp.raise_for_status()
            data = resp.json()

        # HF возвращает список токенов / text
        if isinstance(data, list) and "generated_text" in data[0]:
            return data[0]["generated_text"]

        # Иногда API возвращает другую структуру
        # тогда просто переводим в строку
        return str(data)
