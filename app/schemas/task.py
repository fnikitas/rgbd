from datetime import datetime, date
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field


class TaskBase(BaseModel):
    """Базовая схема задачи."""
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=2000)
    priority: int = Field(default=3, ge=1, le=5)
    theme_id: Optional[UUID] = None
    assignee_id: Optional[UUID] = None
    due_date: Optional[date] = None


class TaskCreate(TaskBase):
    """Схема создания задачи."""
    pass


class TaskUpdate(BaseModel):
    """Схема обновления задачи."""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=2000)
    priority: Optional[int] = Field(None, ge=1, le=5)
    theme_id: Optional[UUID] = None
    assignee_id: Optional[UUID] = None
    due_date: Optional[date] = None


class TaskStatusChange(BaseModel):
    """Схема изменения статуса."""
    to_status: str = Field(..., pattern="^(new|in_progress|done|blocked|canceled)$")


class TaskResponse(TaskBase):
    """Схема ответа задачи."""
    id: UUID
    status: str
    created_by: UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class TaskListResponse(BaseModel):
    """Схема списка задач с пагинацией."""
    items: list[TaskResponse]
    total: int
    limit: int
    offset: int


class TaskStatusHistoryResponse(BaseModel):
    """Схема истории изменения статуса."""
    id: UUID
    task_id: UUID
    from_status: str
    to_status: str
    changed_by: UUID
    changed_at: datetime
    
    class Config:
        from_attributes = True
