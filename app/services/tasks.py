from datetime import date
from typing import Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.history import TaskStatusHistory
from app.models.task import Task
from app.repositories.history import HistoryRepository
from app.repositories.tasks import TaskRepository

VALID_STATUSES = {"new", "in_progress", "done", "blocked", "canceled"}


# Бизнес-логика задач.
class TaskService:
    """Сервис работы с задачами."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = TaskRepository(db)
        self.history_repo = HistoryRepository(db)

    async def create(
        self,
        title: str,
        created_by: UUID,
        description: Optional[str] = None,
        priority: int = 3,
        theme_id: Optional[UUID] = None,
        assignee_id: Optional[UUID] = None,
        due_date: Optional[date] = None,
    ) -> Task:
        """Создать задачу."""
        if priority < 1 or priority > 5:
            raise ValueError("Приоритет должен быть от 1 до 5")

        return await self.repo.create(
            title=title,
            created_by=created_by,
            description=description,
            priority=priority,
            theme_id=theme_id,
            assignee_id=assignee_id,
            due_date=due_date,
        )

    async def get_by_id(self, task_id: UUID) -> Optional[Task]:
        """Получить задачу по идентификатору."""
        return await self.repo.get_by_id(task_id)

    async def update(self, task_id: UUID, **kwargs) -> Optional[Task]:
        """Обновить задачу."""
        if "priority" in kwargs and kwargs["priority"] is not None:
            if kwargs["priority"] < 1 or kwargs["priority"] > 5:
                raise ValueError("Приоритет должен быть от 1 до 5")

        return await self.repo.update(task_id, **kwargs)

    async def delete(self, task_id: UUID) -> bool:
        """Удалить задачу."""
        return await self.repo.delete(task_id)

    async def change_status(
        self,
        task_id: UUID,
        to_status: str,
        changed_by: UUID,
    ) -> Optional[Task]:
        """Изменить статус задачи и записать историю."""
        if to_status not in VALID_STATUSES:
            raise ValueError(f"Недопустимый статус: {to_status}")

        task = await self.get_by_id(task_id)
        if not task:
            return None

        from_status = task.status
        if from_status == to_status:
            return task

        task.status = to_status
        await self.history_repo.create(
            task_id=task_id,
            from_status=from_status,
            to_status=to_status,
            changed_by=changed_by,
            commit=False,
        )
        await self.db.commit()
        await self.db.refresh(task)
        return task

    async def list_with_filters(
        self,
        status: Optional[str] = None,
        theme_id: Optional[UUID] = None,
        assignee_id: Optional[UUID] = None,
        created_by: Optional[UUID] = None,
        priority: Optional[int] = None,
        due_date_from: Optional[date] = None,
        due_date_to: Optional[date] = None,
        q: Optional[str] = None,
        sort: str = "created_at",
        order: str = "desc",
        limit: int = 100,
        offset: int = 0,
    ) -> tuple[list[Task], int]:
        """Получить список задач с фильтрами."""
        return await self.repo.list_with_filters(
            status=status,
            theme_id=theme_id,
            assignee_id=assignee_id,
            created_by=created_by,
            priority=priority,
            due_date_from=due_date_from,
            due_date_to=due_date_to,
            q=q,
            sort=sort,
            order=order,
            limit=limit,
            offset=offset,
        )

    async def get_task_history(self, task_id: UUID) -> list[TaskStatusHistory]:
        """Получить историю смены статусов."""
        return await self.history_repo.get_by_task_id(task_id)
