from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.theme import Theme


class ThemeRepository:
    """Репозиторий для работы с темами."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, theme_id: UUID) -> Optional[Theme]:
        """Получить тему по идентификатору."""
        result = await self.db.execute(select(Theme).where(Theme.id == theme_id))
        return result.scalar_one_or_none()

    async def get_by_name(self, name: str) -> Optional[Theme]:
        """Получить тему по имени."""
        result = await self.db.execute(select(Theme).where(Theme.name == name))
        return result.scalar_one_or_none()

    async def create(self, name: str, description: Optional[str] = None) -> Theme:
        """Создать тему."""
        theme = Theme(name=name, description=description)
        self.db.add(theme)
        await self.db.commit()
        await self.db.refresh(theme)
        return theme

    async def update(self, theme_id: UUID, **kwargs) -> Optional[Theme]:
        """Обновить тему."""
        theme = await self.get_by_id(theme_id)
        if not theme:
            return None

        for key, value in kwargs.items():
            if value is not None:
                setattr(theme, key, value)

        await self.db.commit()
        await self.db.refresh(theme)
        return theme

    async def delete(self, theme_id: UUID) -> bool:
        """Удалить тему."""
        theme = await self.get_by_id(theme_id)
        if not theme:
            return False

        await self.db.delete(theme)
        await self.db.commit()
        return True

    async def list_all(self, limit: int = 100, offset: int = 0) -> tuple[list[Theme], int]:
        """Получить список тем."""
        count_result = await self.db.execute(select(Theme))
        total = len(count_result.all())

        result = await self.db.execute(select(Theme).limit(limit).offset(offset))
        return result.scalars().all(), total

