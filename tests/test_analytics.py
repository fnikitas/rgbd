import pytest
from httpx import AsyncClient


async def create_test_user_with_tasks(client: AsyncClient) -> str:
    """Вспомогательная функция для создания пользователя и задач."""
    await client.post(
        "/auth/register",
        json={
            "email": "test@example.com",
            "username": "testuser",
            "password": "password123",
        },
    )

    login_response = await client.post(
        "/auth/login",
        json={
            "email": "test@example.com",
            "password": "password123",
        },
    )
    token = login_response.json()["access_token"]

    await client.post(
        "/tasks",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "title": "New Task",
            "priority": 3,
        },
    )

    await client.post(
        "/tasks",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "title": "In Progress Task",
            "priority": 2,
        },
    )

    task_id = (
        await client.post(
            "/tasks",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "title": "Done Task",
                "priority": 1,
            },
        )
    ).json()["id"]

    await client.post(
        f"/tasks/{task_id}/status",
        headers={"Authorization": f"Bearer {token}"},
        json={"to_status": "done"},
    )

    return token


@pytest.mark.asyncio
async def test_analytics_summary(client: AsyncClient):
    """Тест эндпоинта сводной аналитики."""
    await create_test_user_with_tasks(client)

    response = await client.get("/analytics/summary")

    assert response.status_code == 200
    data = response.json()

    assert "counts_by_status" in data
    assert "counts_by_theme" in data
    assert "counts_by_assignee" in data
    assert "overdue_count" in data

    assert isinstance(data["counts_by_status"], dict)
    assert isinstance(data["counts_by_theme"], dict)
    assert isinstance(data["counts_by_assignee"], dict)
    assert isinstance(data["overdue_count"], int)


@pytest.mark.asyncio
async def test_analytics_summary_counts(client: AsyncClient):
    """Тест подсчета статусов в аналитике."""
    await create_test_user_with_tasks(client)

    response = await client.get("/analytics/summary")

    assert response.status_code == 200
    data = response.json()

    assert data["counts_by_status"].get("new", 0) == 2
    assert data["counts_by_status"].get("done", 0) == 1


@pytest.mark.asyncio
async def test_analytics_plot_statuses(client: AsyncClient):
    """Тест PNG-графика по статусам."""
    await create_test_user_with_tasks(client)

    response = await client.get("/analytics/plot/statuses.png")

    assert response.status_code == 200
    assert response.headers["content-type"] == "image/png"
    assert len(response.content) > 0


@pytest.mark.asyncio
async def test_analytics_empty_database(client: AsyncClient):
    """Тест аналитики на пустой базе."""
    response = await client.get("/analytics/summary")

    assert response.status_code == 200
    data = response.json()

    assert data["counts_by_status"] == {}
    assert data["counts_by_theme"] == {}
    assert data["counts_by_assignee"] == {}
    assert data["overdue_count"] == 0
