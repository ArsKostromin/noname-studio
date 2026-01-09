# ml_service/services/hf_gpt.py
import httpx
import re
from config import settings


class HFClient:
    def __init__(self, model: str = "zai-org/GLM-4.7"):
        self.model = model
        self.api_url = "https://router.huggingface.co/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {settings.HF_API_KEY}",
            "Content-Type": "application/json",
        }

    async def ask(self, prompt: str) -> str:
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "Ты AI-репетитор. Отвечай коротко и понятно. "
                        "Примеры и аналогии приветствуются. "
                        "Игнорируй сложные детали и reasoning_content. "
                        "Выдавай только один финальный текстовый ответ, "
                        "без списков, шагов, вариантов, нумераций и Markdown."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            "max_tokens": 512,
            "temperature": 0.7,
        }

        async with httpx.AsyncClient(timeout=120) as client:
            resp = await client.post(self.api_url, headers=self.headers, json=payload)

            if resp.status_code != 200:
                raise RuntimeError(f"HF error {resp.status_code}: {resp.text}")

            data = resp.json()
            print("HF RAW RESPONSE:", data)

            text = ""

            # Берем content, если пустой — reasoning_content
            if isinstance(data, dict) and "choices" in data and data["choices"]:
                msg = data["choices"][0].get("message", {})
                text = msg.get("content") or msg.get("reasoning_content") or ""

            # fallback на другие форматы
            if not text:
                if isinstance(data, dict):
                    text = data.get("output") or data.get("generated_text") or ""
                elif isinstance(data, list) and len(data) > 0:
                    text = data[0].get("generated_text") or ""

            text = text.strip()

            # Чистим Markdown, нумерации, переносы и лишние пробелы
            text = re.sub(r"\n\s*\d+\. ?", " ", text)
            text = re.sub(r"\*{1,2}", "", text)
            text = re.sub(r"`.*?`", "", text)
            text = re.sub(r"\n", " ", text)
            text = re.sub(r"\s{2,}", " ", text)
            text = text.strip()

            # 🔹 Оставляем только первую "смысловую часть" до точки, если нужно
            # text = text.split(".")[0] + "."  # Раскомментировать, если короткий ответ нужен

            if not text:
                text = "🤷‍♂️ Модель промолчала, попробуй другой промпт или модель."

            return text
