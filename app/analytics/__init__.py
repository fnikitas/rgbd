"""Инструменты для построения графиков аналитики."""

from app.analytics.plots import (
    HAS_MATPLOTLIB,
    plot_tasks_by_priority,
    plot_tasks_by_status,
    plot_tasks_by_theme,
)

__all__ = [
    "HAS_MATPLOTLIB",
    "plot_tasks_by_status",
    "plot_tasks_by_priority",
    "plot_tasks_by_theme",
]
