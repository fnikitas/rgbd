from pydantic import BaseModel


class TokenResponse(BaseModel):
    """Схема ответа с токеном."""
    access_token: str
    token_type: str = "bearer"


class LoginRequest(BaseModel):
    """Схема запроса для логина."""
    email: str
    password: str


class RegisterRequest(BaseModel):
    """Схема запроса для регистрации."""
    username: str
    email: str
    password: str
