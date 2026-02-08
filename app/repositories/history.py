from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.history import TaskStatusHistory


class HistoryRepository:
    """Репозиторий для истории смены статусов."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        task_id: UUID,
        from_status: str,
        to_status: str,
        changed_by: UUID,
        commit: bool = True,
    ) -> TaskStatusHistory:
        """Создать запись в истории статусов."""
        history = TaskStatusHistory(
            task_id=task_id,
            from_status=from_status,
            to_status=to_status,
            changed_by=changed_by,
        )
        self.db.add(history)
        if commit:
            await self.db.commit()
            await self.db.refresh(history)
        else:
            await self.db.flush()
        return history

    async def get_by_task_id(self, task_id: UUID) -> list[TaskStatusHistory]:
        """Получить историю изменений по задаче."""
        result = await self.db.execute(
            select(TaskStatusHistory)
            .where(TaskStatusHistory.task_id == task_id)
            .order_by(TaskStatusHistory.changed_at.desc())
        )
        return result.scalars().all()
