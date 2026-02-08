from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.task import Task

try:
    import pandas as pd

    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False
    pd = None  # type: ignore


# Сервис для аналитики.
class AnalyticsService:
    """Сервис аналитики."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_summary(self) -> dict:
        """Получить агрегированную аналитику по задачам."""
        result = await self.db.execute(select(Task))
        tasks = result.scalars().all()

        counts_by_status: dict[str, int] = {}
        for task in tasks:
            status = task.status
            counts_by_status[status] = counts_by_status.get(status, 0) + 1

        counts_by_theme: dict[str, int] = {}
        for task in tasks:
            if task.theme_id:
                theme_id = str(task.theme_id)
                counts_by_theme[theme_id] = counts_by_theme.get(theme_id, 0) + 1

        counts_by_assignee: dict[str, int] = {}
        for task in tasks:
            if task.assignee_id:
                assignee_id = str(task.assignee_id)
                counts_by_assignee[assignee_id] = counts_by_assignee.get(assignee_id, 0) + 1

        today = date.today()
        overdue_count = 0
        for task in tasks:
            if task.due_date and task.due_date < today and task.status not in ("done", "canceled"):
                overdue_count += 1

        return {
            "counts_by_status": counts_by_status,
            "counts_by_theme": counts_by_theme,
            "counts_by_assignee": counts_by_assignee,
            "overdue_count": overdue_count,
        }

    async def get_tasks_dataframe(self) -> pd.DataFrame:
        """Собрать таблицу pandas со всеми задачами для графиков."""
        if not HAS_PANDAS:
            raise ImportError(
                "Для аналитики нужен pandas. "
                "Установите зависимости: pip install -e '.[analytics]'"
            )

        result = await self.db.execute(select(Task))
        tasks = result.scalars().all()

        data = []
        for task in tasks:
            data.append(
                {
                    "id": task.id,
                    "title": task.title,
                    "status": task.status,
                    "priority": task.priority,
                    "theme_id": task.theme_id,
                    "assignee_id": task.assignee_id,
                    "created_by": task.created_by,
                    "due_date": task.due_date,
                    "created_at": task.created_at,
                    "updated_at": task.updated_at,
                }
            )

        return pd.DataFrame(data)
