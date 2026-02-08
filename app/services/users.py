from typing import Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password, verify_password
from app.models.user import User
from app.repositories.users import UserRepository


class UserService:
    """Сервис для работы с пользователями."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = UserRepository(db)

    async def register(self, email: str, username: str, password: str) -> User:
        """Зарегистрировать пользователя."""
        existing_user = await self.repo.get_by_email(email)
        if existing_user:
            raise ValueError("Почта уже зарегистрирована")

        hashed_password = hash_password(password)
        return await self.repo.create(email, username, hashed_password)

    async def authenticate(self, email: str, password: str) -> Optional[User]:
        """Проверить логин и пароль пользователя."""
        user = await self.repo.get_by_email(email)
        if not user:
            return None

        if not verify_password(password, user.hashed_password):
            return None

        return user

    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        """Получить пользователя по идентификатору."""
        return await self.repo.get_by_id(user_id)

    async def update(
        self,
        user_id: UUID,
        email: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
    ) -> Optional[User]:
        """Обновить данные пользователя."""
        update_data = {}

        if email:
            existing_user = await self.repo.get_by_email(email)
            if existing_user and existing_user.id != user_id:
                raise ValueError("Почта уже зарегистрирована")
            update_data["email"] = email

        if username:
            update_data["username"] = username

        if password:
            update_data["hashed_password"] = hash_password(password)

        return await self.repo.update(user_id, **update_data)

