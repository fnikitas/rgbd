from datetime import date
from typing import Optional
from uuid import UUID

from sqlalchemy import and_, asc, desc, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.task import Task


ALLOWED_SORT_FIELDS = {"created_at", "due_date", "priority", "status"}
ALLOWED_ORDER = {"asc", "desc"}


class TaskRepository:
    """Репозиторий для работы с задачами."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, task_id: UUID) -> Optional[Task]:
        """Получить задачу по идентификатору."""
        result = await self.db.execute(select(Task).where(Task.id == task_id))
        return result.scalar_one_or_none()

    async def create(
        self,
        title: str,
        created_by: UUID,
        description: Optional[str] = None,
        priority: int = 3,
        theme_id: Optional[UUID] = None,
        assignee_id: Optional[UUID] = None,
        due_date: Optional[date] = None,
        commit: bool = True,
    ) -> Task:
        """Создать задачу."""
        task = Task(
            title=title,
            description=description,
            priority=priority,
            theme_id=theme_id,
            assignee_id=assignee_id,
            created_by=created_by,
            due_date=due_date,
        )
        self.db.add(task)
        if commit:
            await self.db.commit()
            await self.db.refresh(task)
        else:
            await self.db.flush()
        return task

    async def update(self, task_id: UUID, commit: bool = True, **kwargs) -> Optional[Task]:
        """Обновить задачу."""
        task = await self.get_by_id(task_id)
        if not task:
            return None

        clearable_fields = {"description", "theme_id", "assignee_id", "due_date"}
        for key, value in kwargs.items():
            if not hasattr(task, key):
                continue
            if value is None and key not in clearable_fields:
                continue
            setattr(task, key, value)

        if commit:
            await self.db.commit()
            await self.db.refresh(task)
        else:
            await self.db.flush()
        return task

    async def delete(self, task_id: UUID, commit: bool = True) -> bool:
        """Удалить задачу (жесткое удаление)."""
        task = await self.get_by_id(task_id)
        if not task:
            return False

        await self.db.delete(task)
        if commit:
            await self.db.commit()
        else:
            await self.db.flush()
        return True

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
        """Вернуть список задач с фильтрацией, сортировкой и пагинацией."""

        if sort not in ALLOWED_SORT_FIELDS:
            sort = "created_at"
        if order not in ALLOWED_ORDER:
            order = "desc"

        filters = []

        if status:
            filters.append(Task.status == status)
        if theme_id:
            filters.append(Task.theme_id == theme_id)
        if assignee_id:
            filters.append(Task.assignee_id == assignee_id)
        if created_by:
            filters.append(Task.created_by == created_by)
        if priority:
            filters.append(Task.priority == priority)
        if due_date_from:
            filters.append(Task.due_date >= due_date_from)
        if due_date_to:
            filters.append(Task.due_date <= due_date_to)
        if q:
            search_pattern = f"%{q}%"
            filters.append(
                or_(
                    Task.title.ilike(search_pattern),
                    Task.description.ilike(search_pattern),
                )
            )

        query = select(Task)
        if filters:
            query = query.where(and_(*filters))

        count_result = await self.db.execute(query)
        total = len(count_result.all())

        sort_column = getattr(Task, sort)
        if order == "desc":
            query = query.order_by(desc(sort_column))
        else:
            query = query.order_by(asc(sort_column))

        query = query.limit(limit).offset(offset)

        result = await self.db.execute(query)
        return result.scalars().all(), total

