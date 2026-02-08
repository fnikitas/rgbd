from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    """Базовая схема пользователя."""
    email: EmailStr
    username: str


class UserCreate(UserBase):
    """Схема создания пользователя."""
    password: str = Field(..., min_length=8)


class UserUpdate(BaseModel):
    """Схема обновления пользователя."""
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=8)


class UserResponse(UserBase):
    """Схема ответа пользователя."""
    id: UUID
    is_admin: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class UserPublicResponse(BaseModel):
    """Публичная схема пользователя."""
    id: UUID
    username: str
    
    class Config:
        from_attributes = True
