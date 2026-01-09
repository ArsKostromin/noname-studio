# ml_service/services/hf_gpt.py
import httpx
import re
from config import settings
import json

class HFClient:
    # Можно попробовать модель попроще, если GLM-4.7 будет тормозить (например, Qwen/Qwen2.5-72B-Instruct)
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
                    # Инструкция мягче, но четче по формату
                    "content": (
                        "Ты — поддерживающий AI-репетитор. "
                        "Твоя задача: дать короткий, полезный совет студенту на основе его данных. "
                        "Формат ответа: один абзац на русском языке. "
                        "Не используй вводные фразы ('Давай посмотрим', 'Судя по данным'). Сразу к делу."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            # 🔥 ВАЖНО: Увеличили лимит, чтобы хватило на reasoning + ответ
            "max_tokens": 2048,  
            "temperature": 0.6, 
        }

        async with httpx.AsyncClient(timeout=120) as client:
            resp = await client.post(self.api_url, headers=self.headers, json=payload)

            if resp.status_code != 200:
                # Логируем ошибку, но возвращаем заглушку, чтобы фронт не падал
                print(f"HF ERROR: {resp.status_code} {resp.text}")
                return "Сейчас я немного занят вычислениями, спроси меня через минуту."

            data = resp.json()
            # print("HF RAW RESPONSE:", data) # Раскомментируй для дебага
            
            print("\n" + "="*50)
            print("🤖 [OUTPUT] HF RAW RESPONSE:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            print("="*50 + "\n")

            text = ""
            reasoning = ""

            try:
                choice = data["choices"][0]
                msg = choice["message"]
                text = msg.get("content", "").strip()
                reasoning = msg.get("reasoning_content", "").strip()
                
                # Проверка на length (если обрубило даже с 2000 токенов)
                if choice.get("finish_reason") == "length" and not text:
                    print("Warning: Token limit reached during reasoning.")
            except Exception as e:
                print(f"Error parsing response: {e}")

            # 1. Идеальный сценарий: есть готовый ответ
            if text:
                return text

            # 2. Если ответа нет (съело лимит), пробуем вытащить из рассуждений
            if reasoning:
                extracted = self._extract_final_advice(reasoning)
                if extracted:
                    return extracted

            # 3. Фолбек
            return "Давай начнём с самых простых примеров и разберём их вместе, шаг за шагом."

    def _extract_final_advice(self, reasoning: str) -> str:
        """Попытка спасти ответ, если модель написала его в конце мыслей"""
        # Убираем маркдаун болд/курсив
        clean_text = re.sub(r"\*\*|\*", "", reasoning)
        
        # Разбиваем на строки и ищем те, где есть кириллица
        lines = [l.strip() for l in clean_text.split("\n") if l.strip()]
        russian_lines = [l for l in lines if re.search(r"[А-Яа-я]", l)]

        if not russian_lines:
            return ""

        # Берем последнюю содержательную русскую фразу
        # Часто модели пишут "Output: ..." или "Response: ..." в конце мыслей
        candidate = russian_lines[-1]
        
        # Если строка слишком короткая (менее 20 символов), берем две последние
        if len(candidate) < 20 and len(russian_lines) > 1:
            candidate = russian_lines[-2] + " " + candidate

        # Чистим мусор в начале строки (типа "Совет:", "Ответ:", "Draft:")
        candidate = re.sub(r"^(совет|ответ|draft|output|result)[\s:]*", "", candidate, flags=re.IGNORECASE)
        
        return candidate.strip()