from typing import Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.theme import Theme
from app.repositories.themes import ThemeRepository


class ThemeService:
    """Сервис для работы с темами."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = ThemeRepository(db)

    async def create(self, name: str, description: Optional[str] = None) -> Theme:
        """Создать тему."""
        existing_theme = await self.repo.get_by_name(name)
        if existing_theme:
            raise ValueError("Тема с таким именем уже есть")

        return await self.repo.create(name, description)

    async def get_by_id(self, theme_id: UUID) -> Optional[Theme]:
        """Получить тему по идентификатору."""
        return await self.repo.get_by_id(theme_id)

    async def update(
        self,
        theme_id: UUID,
        name: Optional[str] = None,
        description: Optional[str] = None,
    ) -> Optional[Theme]:
        """Обновить тему."""
        if name:
            existing_theme = await self.repo.get_by_name(name)
            if existing_theme and existing_theme.id != theme_id:
                raise ValueError("Тема с таким именем уже есть")

        update_data = {}
        if name:
            update_data["name"] = name
        if description is not None:
            update_data["description"] = description

        return await self.repo.update(theme_id, **update_data)

    async def delete(self, theme_id: UUID) -> bool:
        """Удалить тему."""
        return await self.repo.delete(theme_id)

    async def list_all(self, limit: int = 100, offset: int = 0) -> tuple[list[Theme], int]:
        """Получить список тем."""
        return await self.repo.list_all(limit, offset)

