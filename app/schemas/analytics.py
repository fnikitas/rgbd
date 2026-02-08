from pydantic import BaseModel


class AnalyticsSummary(BaseModel):
    """Схема аналитики."""
    counts_by_status: dict[str, int]
    counts_by_theme: dict[str, int]
    counts_by_assignee: dict[str, int]
    overdue_count: int
