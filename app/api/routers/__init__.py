"""Набор веб-роутеров."""

from app.api.routers import analytics, auth, tasks, themes, users

__all__ = ["auth", "users", "themes", "tasks", "analytics"]
