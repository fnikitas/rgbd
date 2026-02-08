from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


class UserRepository:
    """Репозиторий для работы с пользователями."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        """Получить пользователя по идентификатору."""
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> Optional[User]:
        """Получить пользователя по почте."""
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def create(
        self,
        email: str,
        username: str,
        hashed_password: str,
        is_admin: bool = False,
    ) -> User:
        """Создать пользователя."""
        user = User(
            email=email,
            username=username,
            hashed_password=hashed_password,
            is_admin=is_admin,
        )
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def update(self, user_id: UUID, **kwargs) -> Optional[User]:
        """Обновить пользователя."""
        user = await self.get_by_id(user_id)
        if not user:
            return None

        for key, value in kwargs.items():
            if value is not None:
                setattr(user, key, value)

        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def list_all(self, limit: int = 100, offset: int = 0) -> tuple[list[User], int]:
        """Получить список пользователей."""
        count_result = await self.db.execute(select(User))
        total = len(count_result.all())

        result = await self.db.execute(select(User).limit(limit).offset(offset))
        return result.scalars().all(), total

