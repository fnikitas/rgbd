import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Index, String

from app.db.base import Base
from app.db.types import GUID


class TaskStatusHistory(Base):
    """Модель истории изменения статуса задачи."""

    __tablename__ = "task_status_history"
    __table_args__ = (Index("idx_history_task_id", "task_id"),)

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    task_id = Column(GUID(), ForeignKey("tasks.id"), nullable=False)
    from_status = Column(String(20), nullable=False)
    to_status = Column(String(20), nullable=False)
    changed_by = Column(GUID(), ForeignKey("users.id"), nullable=False)
    changed_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self) -> str:
        return f"<TaskStatusHistory {self.task_id}>"
