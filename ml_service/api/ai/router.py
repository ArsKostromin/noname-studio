# ml_service/api/ai/router.py
from fastapi import APIRouter
from pydantic import BaseModel
from services.hf_gpt import HFClient

hf_client = HFClient()

router = APIRouter(prefix="/api/ai", tags=["ai"])


# Pydantic модель для тела запроса
class HFRequest(BaseModel):
    prompt: str


class HFResponse(BaseModel):
    answer: str


@router.post("/hf/test", response_model=HFResponse)
async def hf_test(payload: HFRequest):
    """
    Получает текст в теле запроса и отдает ответ нейронки.
    POST body example (JSON):
    {
        "prompt": "Объясни интегралы простыми словами"
    }
    """
    text = await hf_client.ask(payload.prompt)
    return HFResponse(answer=text)
