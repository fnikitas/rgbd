import io
from typing import Optional

import pandas as pd

try:
    from matplotlib import pyplot as plt

    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False


def plot_tasks_by_status(df: pd.DataFrame) -> Optional[bytes]:
    """Построить PNG-график количества задач по статусам."""
    if not HAS_MATPLOTLIB:
        raise ImportError(
            "Для построения графиков нужен matplotlib. "
            "Установите зависимости: pip install -e '.[analytics]'"
        )

    status_counts = df["status"].value_counts()

    fig, ax = plt.subplots(figsize=(10, 6))
    status_counts.plot(kind="bar", ax=ax, color="steelblue")

    ax.set_title("Задачи по статусам", fontsize=16, fontweight="bold")
    ax.set_xlabel("Статус", fontsize=12)
    ax.set_ylabel("Количество", fontsize=12)
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha="right")

    for i, value in enumerate(status_counts):
        ax.text(i, value + 0.1, str(value), ha="center", fontsize=10)

    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format="png", dpi=100)
    buf.seek(0)
    plt.close(fig)

    return buf.getvalue()


def plot_tasks_by_priority(df: pd.DataFrame) -> Optional[bytes]:
    """Построить PNG-график количества задач по приоритетам."""
    if not HAS_MATPLOTLIB:
        raise ImportError(
            "Для построения графиков нужен matplotlib. "
            "Установите зависимости: pip install -e '.[analytics]'"
        )

    priority_counts = df["priority"].value_counts().sort_index()

    fig, ax = plt.subplots(figsize=(10, 6))
    priority_counts.plot(kind="bar", ax=ax, color="coral")

    ax.set_title("Задачи по приоритетам", fontsize=16, fontweight="bold")
    ax.set_xlabel("Приоритет", fontsize=12)
    ax.set_ylabel("Количество", fontsize=12)
    ax.set_xticklabels(ax.get_xticklabels(), rotation=0)

    for i, value in enumerate(priority_counts):
        ax.text(i, value + 0.1, str(value), ha="center", fontsize=10)

    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format="png", dpi=100)
    buf.seek(0)
    plt.close(fig)

    return buf.getvalue()


def plot_tasks_by_theme(df: pd.DataFrame) -> Optional[bytes]:
    """Построить PNG-график количества задач по темам."""
    if not HAS_MATPLOTLIB:
        raise ImportError(
            "Для построения графиков нужен matplotlib. "
            "Установите зависимости: pip install -e '.[analytics]'"
        )

    theme_counts = df[df["theme_id"].notna()]["theme_id"].value_counts().head(10)

    if len(theme_counts) == 0:
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.text(0.5, 0.5, "Нет задач с темами", ha="center", va="center", fontsize=14)
        ax.set_title("Задачи по темам", fontsize=16, fontweight="bold")
        ax.axis("off")
    else:
        fig, ax = plt.subplots(figsize=(10, 6))
        theme_counts.plot(kind="bar", ax=ax, color="mediumseagreen")

        ax.set_title("Задачи по темам (топ 10)", fontsize=16, fontweight="bold")
        ax.set_xlabel("ID темы", fontsize=12)
        ax.set_ylabel("Количество", fontsize=12)
        ax.set_xticklabels([str(x)[:8] for x in theme_counts.index], rotation=45, ha="right")

        for i, value in enumerate(theme_counts):
            ax.text(i, value + 0.1, str(value), ha="center", fontsize=10)

    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format="png", dpi=100)
    buf.seek(0)
    plt.close(fig)

    return buf.getvalue()
