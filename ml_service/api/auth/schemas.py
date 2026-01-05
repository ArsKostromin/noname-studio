from pydantic import BaseModel


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    access: str
    refresh: str
    user_id: str
    username: str
    full_name: str


class RefreshRequest(BaseModel):
    refresh: str


class RefreshResponse(BaseModel):
    access: str
    refresh: str
