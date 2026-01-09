# ml_service/api/ai/router.py
from fastapi import APIRouter
from pydantic import BaseModel
from services.hf_gpt import HFClient
from services.features import collect_student_features
from services.ml_model import predict_topic_needs

router = APIRouter(prefix="/api/ai", tags=["ai"])
hf_client = HFClient()


# ======================
# Pydantic модели
# ======================
class AIMessageRequest(BaseModel):
    access_token: str
    message: str


class AIMessageResponse(BaseModel):
    message: str


# ======================
# helpers
# ======================
def build_student_context(features: dict, ml_results: dict) -> str:
    parts = []

    for topic, data in features.items():
        avg = data.get("avg_score")
        fails = data.get("fails")
        days = data.get("days_until_event")
        is_test = data.get("is_test")
        is_exam = data.get("is_exam")

        line = f"Тема: {topic}. "
        if avg is not None:
            line += f"Средняя оценка {avg}. "
        if fails:
            line += f"Провалов {fails}. "
        if days is not None:
            if is_exam:
                line += f"Экзамен через {days} дней. "
            elif is_test:
                line += f"Контрольная через {days} дней. "

        parts.append(line)

    for topic, ml in ml_results.items():
        if ml.get("need_review"):
            parts.append(f"По теме {topic} модель советует повторить материал.")

    return " ".join(parts)


# ======================
# Эндпоинт
# ======================
@router.post("/message", response_model=AIMessageResponse)
async def message(payload: AIMessageRequest):
    features = await collect_student_features(payload.access_token)
    ml_results = predict_topic_needs(features)
    student_context = build_student_context(features, ml_results)

    # Упрощенный промпт
    prompt = f"""
Информация о студенте:
{student_context}

Вопрос студента:
"{payload.message}"

Напиши один совет (30-50 слов) для этого студента на русском языке.
Совет должен быть конкретным и мотивирующим.
Если данных по другим предметам нет, опирайся только на то, что известно (например, {student_context}).
"""
# 🔥 ЛОГИРОВАНИЕ ЗАПРОСА (INPUT)
    print("\n" + "="*50)
    print("🚀 [INPUT] CONTEXT & PROMPT:")
    print(f"Context: {student_context}")
    print("-" * 20)
    print(f"User Msg: {payload.message}")
    print("="*50 + "\n")
    
    ai_response = await hf_client.ask(prompt)

    return AIMessageResponse(message=ai_response)