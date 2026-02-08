from datetime import datetime, date
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field


class ThemeBase(BaseModel):
    """Базовая схема темы."""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1024)


class ThemeCreate(ThemeBase):
    """Схема создания темы."""
    pass


class ThemeUpdate(BaseModel):
    """Схема обновления темы."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1024)


class ThemeResponse(ThemeBase):
    """Схема ответа темы."""
    id: UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
