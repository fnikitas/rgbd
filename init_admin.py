"""Скрипт для создания администратора."""

import asyncio
import os
import sys

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.core.config import settings
from app.core.security import hash_password
from app.models import User


async def init_admin():
    """Создать пользователя-админа, если его нет."""
    engine = create_async_engine(settings.DATABASE_URL, future=True)
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        from sqlalchemy import select

        result = await session.execute(select(User).where(User.email == "admin@example.com"))
        admin = result.scalar_one_or_none()

        if admin:
            print("Админ уже существует")
            return

        admin_user = User(
            email="admin@example.com",
            username="admin",
            hashed_password=hash_password("admin123"),
            is_admin=True,
        )
        session.add(admin_user)
        await session.commit()
        print("Админ создан: admin@example.com (пароль: admin123)")
        print("Важно: поменяйте пароль админа на проде")


if __name__ == "__main__":
    asyncio.run(init_admin())
