# ml_service/services/hf_gpt.py

import httpx
import re
import json
import time
from typing import AsyncGenerator
from config import settings


class HFClient:
    def __init__(self, model: str = "zai-org/GLM-4.7"):
        self.model = model
        self.api_url = "https://router.huggingface.co/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {settings.HF_API_KEY}",
            "Content-Type": "application/json",
        }

    # =========================
    # Обычный НЕстрим запрос
    # =========================
    async def ask(self, prompt: str) -> str:
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "Ты — поддерживающий AI-репетитор. "
                        "Дай короткий, полезный совет студенту. "
                        "Один абзац, на русском, сразу к делу."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            "max_tokens": 1024,
            "temperature": 0.6,
        }

        async with httpx.AsyncClient(timeout=120) as client:
            resp = await client.post(self.api_url, headers=self.headers, json=payload)

            if resp.status_code != 200:
                print(f"HF ERROR: {resp.status_code} {resp.text}")
                return "Сейчас я занят вычислениями, попробуй чуть позже."

            data = resp.json()

            try:
                choice = data["choices"][0]
                msg = choice["message"]
                text = msg.get("content", "").strip()
                if text:
                    return text
            except Exception as e:
                print(f"HF parse error: {e}")

            return "Давай начнём с самых простых примеров и разберём их шаг за шагом."

    # =========================
    # СТРИМ как в ChatGPT
    # =========================
    async def ask_stream(self, prompt: str) -> AsyncGenerator[str, None]:
        """
        Возвращает ЧИСТЫЙ ТЕКСТ по кускам.
        Никаких data:, никаких JSON — только символы ответа.
        """

        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "Ты — поддерживающий AI-репетитор. "
                        "Дай короткий, полезный совет студенту. "
                        "Один абзац, на русском, сразу к делу. "
                        "Можно использовать Markdown."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            "max_tokens": 1024,
            "temperature": 0.7,
            "stream": True,
        }

        start_time = time.time()
        first_chunk_time = None
        full_response = ""
        chunk_count = 0
        line_count = 0

        print(f"🚀 [HF_STREAM] Начало запроса к HuggingFace")
        print(f"🚀 [HF_STREAM] Model: {self.model}")
        print(f"🚀 [HF_STREAM] URL: {self.api_url}")

        async with httpx.AsyncClient(timeout=None) as client:
            try:
                async with client.stream(
                    "POST", self.api_url, headers=self.headers, json=payload
                ) as response:

                    print(f"📡 [HF_STREAM] HTTP Status: {response.status_code}")

                    if response.status_code != 200:
                        err = await response.aread()
                        msg = f"HF STREAM ERROR {response.status_code}: {err.decode()}"
                        print(f"❌ [HF_STREAM] {msg}")
                        yield "Ошибка генерации ответа."
                        return

                    print(f"📥 [HF_STREAM] Начинаем чтение строк...")
                    async for line in response.aiter_lines():
                        line_count += 1
                        
                        if not line:
                            continue

                        # Логируем первые несколько строк для отладки
                        if line_count <= 5:
                            print(f"📄 [HF_STREAM] Line #{line_count}: {line[:100]}...")

                        # HF шлёт SSE:  data: {...} или data: {...}
                        # Проверяем оба варианта: "data:" и "data: "
                        if line.startswith("data: "):
                            data_str = line[6:].strip()  # Убираем "data: " и пробелы
                        elif line.startswith("data:"):
                            data_str = line[5:].strip()  # Убираем "data:" и пробелы
                        else:
                            if line_count <= 10:
                                print(f"⏭️ [HF_STREAM] Пропуск строки (не начинается с 'data:'): {line[:50]}...")
                            continue

                        if data_str == "[DONE]":
                            print(f"🏁 [HF_STREAM] Получен сигнал [DONE]")
                            break

                        try:
                            data_json = json.loads(data_str)
                        except json.JSONDecodeError as e:
                            if line_count <= 10:
                                print(f"⚠️ [HF_STREAM] Ошибка парсинга JSON: {e}, data_str: {data_str[:100]}")
                            continue

                        choices = data_json.get("choices", [])
                        if not choices:
                            if line_count <= 10:
                                print(f"⚠️ [HF_STREAM] Нет choices в ответе: {data_json}")
                            continue

                        delta = choices[0].get("delta", {})

                        # ❗ Берём ТОЛЬКО content, reasoning выкидываем нахер
                        content = delta.get("content", "")
                        reasoning = delta.get("reasoning_content", "")

                        if reasoning:
                            if first_chunk_time is None:
                                elapsed = time.time() - start_time
                                print(f"💭 [HF_STREAM] Получен reasoning @ {elapsed:.2f}s: {reasoning[:50]}...")

                        if content:
                            if first_chunk_time is None:
                                first_chunk_time = time.time() - start_time
                                print(f"✅ [HF_STREAM] FIRST CONTENT TOKEN @ {first_chunk_time:.2f}s: '{content[:50]}...'")

                            full_response += content
                            chunk_count += 1

                            # Логируем первые несколько чанков
                            if chunk_count <= 5:
                                print(f"📦 [HF_STREAM] Chunk #{chunk_count}: '{content[:50]}...' (всего {len(full_response)} символов)")

                            # 🔥 ВОТ ЭТО УЛЕТАЕТ НА ФРОНТ
                            yield content

            except Exception as e:
                print(f"❌ [HF_STREAM] EXCEPTION: {e}")
                import traceback
                traceback.print_exc()
                yield "Ошибка соединения с моделью."

        total_time = time.time() - start_time
        print("\n" + "=" * 50)
        print("🤖 [HF_STREAM] STREAM FINISHED")
        print(f"📊 [HF_STREAM] Всего строк обработано: {line_count}")
        print(
            f"⏱️ [HF_STREAM] Первый чанк: {first_chunk_time:.2f}s"
            if first_chunk_time
            else "⏱️ [HF_STREAM] Первый чанк: не получен"
        )
        print(f"📦 [HF_STREAM] Всего чанков: {chunk_count}")
        print(f"⏱️ [HF_STREAM] Общее время: {total_time:.2f}s")
        print(f"📝 [HF_STREAM] Длина ответа: {len(full_response)} символов")
        if full_response:
            print(f"📄 [HF_STREAM] Полный ответ:")
            print(full_response[:500] + ("..." if len(full_response) > 500 else ""))
        else:
            print(f"⚠️ [HF_STREAM] ВНИМАНИЕ: Пустой ответ!")
        print("=" * 50 + "\n")
