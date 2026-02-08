import uuid
from datetime import datetime

from sqlalchemy import CheckConstraint, Column, Date, DateTime, ForeignKey, Index, Integer, String

from app.db.base import Base
from app.db.types import GUID


class Task(Base):
    """Модель задачи."""

    __tablename__ = "tasks"
    __table_args__ = (
        CheckConstraint("status IN ('new', 'in_progress', 'done', 'blocked', 'canceled')", name="check_task_status"),
        CheckConstraint("priority >= 1 AND priority <= 5", name="check_task_priority"),
        Index("idx_tasks_status", "status"),
        Index("idx_tasks_assignee_id", "assignee_id"),
        Index("idx_tasks_theme_id", "theme_id"),
        Index("idx_tasks_due_date", "due_date"),
        Index("idx_tasks_status_assignee_id", "status", "assignee_id"),
    )

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    title = Column(String(255), nullable=False)
    description = Column(String(2000), nullable=True)
    status = Column(String(20), default="new", nullable=False)  # Код статуса задачи.
    priority = Column(Integer, default=3, nullable=False)  # Приоритет от 1 до 5.
    theme_id = Column(GUID(), ForeignKey("themes.id"), nullable=True)
    assignee_id = Column(GUID(), ForeignKey("users.id"), nullable=True)
    created_by = Column(GUID(), ForeignKey("users.id"), nullable=False)
    due_date = Column(Date, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self) -> str:
        return f"<Task {self.title}>"
