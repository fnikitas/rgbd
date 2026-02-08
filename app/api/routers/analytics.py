from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.analytics.plots import HAS_MATPLOTLIB, plot_tasks_by_status
from app.core.deps import get_db
from app.schemas.analytics import AnalyticsSummary
from app.services.analytics import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/summary", response_model=AnalyticsSummary)
async def get_analytics_summary(
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Вернуть сводную аналитику по задачам."""
    service = AnalyticsService(db)
    summary = await service.get_summary()
    return summary


@router.get("/plot/statuses.png")
async def get_plot_statuses(
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Вернуть PNG-график по количеству задач в статусах."""
    if not HAS_MATPLOTLIB:
        return StreamingResponse(
            iter(["matplotlib не установлен".encode("utf-8")]),
            media_type="text/plain; charset=utf-8",
            status_code=503,
        )

    service = AnalyticsService(db)
    df = await service.get_tasks_dataframe()

    if len(df) == 0:
        import io

        try:
            from matplotlib import pyplot as plt

            fig, ax = plt.subplots(figsize=(10, 6))
            ax.text(0.5, 0.5, "Данных по задачам пока нет", ha="center", va="center", fontsize=14)
            ax.set_title("Задачи по статусам", fontsize=16, fontweight="bold")
            ax.axis("off")

            buf = io.BytesIO()
            plt.savefig(buf, format="png", dpi=100)
            buf.seek(0)
            plt.close(fig)
            png_data = buf.getvalue()
        except ImportError:
            return StreamingResponse(
                iter(["matplotlib не установлен".encode("utf-8")]),
                media_type="text/plain; charset=utf-8",
                status_code=503,
            )
    else:
        png_data = plot_tasks_by_status(df)

    return StreamingResponse(
        iter([png_data]),
        media_type="image/png",
        headers={"Content-Disposition": "inline; filename=statuses.png"},
    )
