from pydantic import BaseModel

class AIMessageRequest(BaseModel):
    message: str   # любое сообщение от студента
    access_token: str  # токен для доступа к my-grades и my-schedule

class AIMessageResponse(BaseModel):
    message: str
