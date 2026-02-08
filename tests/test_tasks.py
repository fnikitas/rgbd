from datetime import date, timedelta

import pytest
from httpx import AsyncClient


async def create_test_user(
    client: AsyncClient,
    email: str = "test@example.com",
    username: str = "testuser",
) -> tuple[str, str]:
    """Вспомогательная функция: зарегистрировать пользователя и взять токен."""
    reg_response = await client.post(
        "/auth/register",
        json={
            "email": email,
            "username": username,
            "password": "password123",
        },
    )
    user_id = reg_response.json()["id"]

    login_response = await client.post(
        "/auth/login",
        json={
            "email": email,
            "password": "password123",
        },
    )
    token = login_response.json()["access_token"]

    return token, user_id


@pytest.mark.asyncio
async def test_create_task(client: AsyncClient):
    """Тест создания задачи."""
    token, _ = await create_test_user(client)

    response = await client.post(
        "/tasks",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "title": "Test Task",
            "description": "This is a test task",
            "priority": 3,
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Test Task"
    assert data["description"] == "This is a test task"
    assert data["priority"] == 3
    assert data["status"] == "new"
    assert "id" in data


@pytest.mark.asyncio
async def test_get_task(client: AsyncClient):
    """Тест получения задачи по идентификатору."""
    token, _ = await create_test_user(client)

    create_response = await client.post(
        "/tasks",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "title": "Test Task",
            "priority": 3,
        },
    )
    task_id = create_response.json()["id"]

    response = await client.get(f"/tasks/{task_id}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == task_id
    assert data["title"] == "Test Task"


@pytest.mark.asyncio
async def test_update_task(client: AsyncClient):
    """Тест обновления задачи."""
    token, _ = await create_test_user(client)

    create_response = await client.post(
        "/tasks",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "title": "Test Task",
            "priority": 3,
        },
    )
    task_id = create_response.json()["id"]

    response = await client.patch(
        f"/tasks/{task_id}",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "title": "Updated Task",
            "priority": 5,
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Task"
    assert data["priority"] == 5


@pytest.mark.asyncio
async def test_delete_task(client: AsyncClient):
    """Тест удаления задачи."""
    token, _ = await create_test_user(client)

    create_response = await client.post(
        "/tasks",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "title": "Test Task",
            "priority": 3,
        },
    )
    task_id = create_response.json()["id"]

    response = await client.delete(
        f"/tasks/{task_id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 204

    get_response = await client.get(f"/tasks/{task_id}")
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_list_tasks(client: AsyncClient):
    """Тест получения списка задач."""
    token, _ = await create_test_user(client)

    for i in range(3):
        await client.post(
            "/tasks",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "title": f"Task {i}",
                "priority": i + 1,
            },
        )

    response = await client.get("/tasks")

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 3
    assert len(data["items"]) == 3


@pytest.mark.asyncio
async def test_list_tasks_with_filters(client: AsyncClient):
    """Тест фильтрации задач."""
    token, _ = await create_test_user(client)

    await client.post(
        "/tasks",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "title": "High Priority Task",
            "priority": 5,
        },
    )
    await client.post(
        "/tasks",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "title": "Low Priority Task",
            "priority": 1,
        },
    )

    response = await client.get("/tasks?priority=5")

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["priority"] == 5


@pytest.mark.asyncio
async def test_list_tasks_search(client: AsyncClient):
    """Тест поиска по названию и описанию."""
    token, _ = await create_test_user(client)

    await client.post(
        "/tasks",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "title": "Python development",
            "priority": 3,
        },
    )
    await client.post(
        "/tasks",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "title": "JavaScript task",
            "priority": 3,
        },
    )

    response = await client.get("/tasks?q=Python")

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert "Python" in data["items"][0]["title"]


@pytest.mark.asyncio
async def test_change_task_status(client: AsyncClient):
    """Тест изменения статуса задачи."""
    token, _ = await create_test_user(client)

    create_response = await client.post(
        "/tasks",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "title": "Test Task",
            "priority": 3,
        },
    )
    task_id = create_response.json()["id"]

    response = await client.post(
        f"/tasks/{task_id}/status",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "to_status": "in_progress",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "in_progress"


@pytest.mark.asyncio
async def test_task_status_history(client: AsyncClient):
    """Тест истории изменения статуса."""
    token, _ = await create_test_user(client)

    create_response = await client.post(
        "/tasks",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "title": "Test Task",
            "priority": 3,
        },
    )
    task_id = create_response.json()["id"]

    await client.post(
        f"/tasks/{task_id}/status",
        headers={"Authorization": f"Bearer {token}"},
        json={"to_status": "in_progress"},
    )
    await client.post(
        f"/tasks/{task_id}/status",
        headers={"Authorization": f"Bearer {token}"},
        json={"to_status": "done"},
    )

    response = await client.get(
        f"/tasks/{task_id}/history",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["to_status"] == "done"
    assert data[1]["to_status"] == "in_progress"


@pytest.mark.asyncio
async def test_task_ownership(client: AsyncClient):
    """Тест проверки прав на редактирование задачи."""
    token1, _ = await create_test_user(client, email="user1@example.com", username="user1")
    token2, _ = await create_test_user(client, email="user2@example.com", username="user2")

    create_response = await client.post(
        "/tasks",
        headers={"Authorization": f"Bearer {token1}"},
        json={
            "title": "User1 Task",
            "priority": 3,
        },
    )
    task_id = create_response.json()["id"]

    response = await client.patch(
        f"/tasks/{task_id}",
        headers={"Authorization": f"Bearer {token2}"},
        json={"title": "Modified"},
    )

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_tasks_crud(client: AsyncClient):
    """Полный сценарий создания, чтения, обновления и удаления задач."""
    token, _ = await create_test_user(client, email="crud@example.com", username="crud")

    create_response = await client.post(
        "/tasks",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "title": "CRUD Task",
            "description": "Initial",
            "priority": 3,
        },
    )
    assert create_response.status_code == 200
    task_id = create_response.json()["id"]

    get_response = await client.get(f"/tasks/{task_id}")
    assert get_response.status_code == 200

    update_response = await client.patch(
        f"/tasks/{task_id}",
        headers={"Authorization": f"Bearer {token}"},
        json={"title": "Updated CRUD Task", "priority": 5},
    )
    assert update_response.status_code == 200
    assert update_response.json()["priority"] == 5

    delete_response = await client.delete(
        f"/tasks/{task_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert delete_response.status_code == 204

    missing_response = await client.get(f"/tasks/{task_id}")
    assert missing_response.status_code == 404


@pytest.mark.asyncio
async def test_tasks_filtering_sorting(client: AsyncClient):
    """Проверка фильтрации и сортировки списка задач."""
    token, _ = await create_test_user(client, email="filter@example.com", username="filter")

    await client.post(
        "/tasks",
        headers={"Authorization": f"Bearer {token}"},
        json={"title": "P5", "priority": 5},
    )
    await client.post(
        "/tasks",
        headers={"Authorization": f"Bearer {token}"},
        json={"title": "P1", "priority": 1},
    )
    await client.post(
        "/tasks",
        headers={"Authorization": f"Bearer {token}"},
        json={"title": "P3", "priority": 3},
    )

    filter_response = await client.get("/tasks?priority=5")
    assert filter_response.status_code == 200
    filter_data = filter_response.json()
    assert filter_data["total"] == 1
    assert filter_data["items"][0]["priority"] == 5

    sort_response = await client.get("/tasks?sort=priority&order=asc")
    assert sort_response.status_code == 200
    sort_data = sort_response.json()
    priorities = [item["priority"] for item in sort_data["items"]]
    assert priorities == sorted(priorities)


@pytest.mark.asyncio
async def test_task_status_change_creates_history(client: AsyncClient):
    """Проверка, что смена статуса создает запись в истории."""
    token, _ = await create_test_user(client, email="history@example.com", username="history")

    create_response = await client.post(
        "/tasks",
        headers={"Authorization": f"Bearer {token}"},
        json={"title": "History Task", "priority": 3},
    )
    task_id = create_response.json()["id"]

    status_response = await client.post(
        f"/tasks/{task_id}/status",
        headers={"Authorization": f"Bearer {token}"},
        json={"to_status": "in_progress"},
    )
    assert status_response.status_code == 200

    history_response = await client.get(
        f"/tasks/{task_id}/history",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert history_response.status_code == 200
    history = history_response.json()
    assert len(history) == 1
    assert history[0]["from_status"] == "new"
    assert history[0]["to_status"] == "in_progress"


@pytest.mark.asyncio
async def test_task_status_change_permission_denied(client: AsyncClient):
    """Проверка, что менять статус может только владелец или админ."""
    token1, _ = await create_test_user(client, email="owner@example.com", username="owner")
    token2, _ = await create_test_user(client, email="other@example.com", username="other")

    create_response = await client.post(
        "/tasks",
        headers={"Authorization": f"Bearer {token1}"},
        json={"title": "Owner Task", "priority": 3},
    )
    task_id = create_response.json()["id"]

    response = await client.post(
        f"/tasks/{task_id}/status",
        headers={"Authorization": f"Bearer {token2}"},
        json={"to_status": "in_progress"},
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_task_history_permissions(client: AsyncClient):
    """Проверка прав на просмотр истории: автор, исполнитель или админ."""
    token1, user1_id = await create_test_user(client, email="author@example.com", username="author")
    token2, user2_id = await create_test_user(client, email="assignee@example.com", username="assignee")
    token3, _ = await create_test_user(client, email="other3@example.com", username="other3")

    create_response = await client.post(
        "/tasks",
        headers={"Authorization": f"Bearer {token1}"},
        json={
            "title": "History Task",
            "priority": 3,
            "assignee_id": user2_id,
        },
    )
    task_id = create_response.json()["id"]

    await client.post(
        f"/tasks/{task_id}/status",
        headers={"Authorization": f"Bearer {token1}"},
        json={"to_status": "in_progress"},
    )

    author_resp = await client.get(
        f"/tasks/{task_id}/history",
        headers={"Authorization": f"Bearer {token1}"},
    )
    assert author_resp.status_code == 200

    assignee_resp = await client.get(
        f"/tasks/{task_id}/history",
        headers={"Authorization": f"Bearer {token2}"},
    )
    assert assignee_resp.status_code == 200

    other_resp = await client.get(
        f"/tasks/{task_id}/history",
        headers={"Authorization": f"Bearer {token3}"},
    )
    assert other_resp.status_code == 403

