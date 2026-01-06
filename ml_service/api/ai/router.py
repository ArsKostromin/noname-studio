from fastapi import APIRouter
from api.ai.schemas import AIMessageRequest, AIMessageResponse
from services.core_api import CoreAPIClient
from services.features import extract_grade_features, extract_schedule_features, collect_student_features
from ml_service.ml_model import predict_topic_needs  # LogisticRegression + KMeans
from services.yandex_gpt import ask_yandex_gpt  # обёртка для GPT

router = APIRouter(prefix="/api/ai", tags=["ai"])

@router.post("/message", response_model=AIMessageResponse)
async def message(payload: AIMessageRequest):
    # 1️⃣ Собираем фичи студента
    features = await collect_student_features(payload.access_token)

    # 2️⃣ Прогоняем через ML
    ml_results = predict_topic_needs(features)

    # 3️⃣ Формируем промпт для GPT
    prompt = f"""
    У студента следующие показатели по темам:
    {ml_results}

    Ответь на вопрос студента "{payload.message}" простым языком, дай советы, что подтянуть.
    """
    ai_response = await ask_yandex_gpt(prompt)

    return AIMessageResponse(message=ai_response)
