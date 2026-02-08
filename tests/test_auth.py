import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register(client: AsyncClient):
    """Тест регистрации пользователя."""
    response = await client.post(
        "/auth/register",
        json={
            "email": "test@example.com",
            "username": "testuser",
            "password": "password123",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["username"] == "testuser"
    assert "id" in data
    assert "created_at" in data


@pytest.mark.asyncio
async def test_register_duplicate_email(client: AsyncClient):
    """Тест регистрации с дублирующейся почтой."""
    await client.post(
        "/auth/register",
        json={
            "email": "test@example.com",
            "username": "testuser",
            "password": "password123",
        },
    )

    response = await client.post(
        "/auth/register",
        json={
            "email": "test@example.com",
            "username": "another",
            "password": "password123",
        },
    )

    assert response.status_code == 400


@pytest.mark.asyncio
async def test_login(client: AsyncClient):
    """Тест входа."""
    await client.post(
        "/auth/register",
        json={
            "email": "test@example.com",
            "username": "testuser",
            "password": "password123",
        },
    )

    response = await client.post(
        "/auth/login",
        json={
            "email": "test@example.com",
            "password": "password123",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient):
    """Тест входа с неправильным паролем."""
    await client.post(
        "/auth/register",
        json={
            "email": "test@example.com",
            "username": "testuser",
            "password": "password123",
        },
    )

    response = await client.post(
        "/auth/login",
        json={
            "email": "test@example.com",
            "password": "wrongpassword",
        },
    )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_me(client: AsyncClient):
    """Тест получения текущего пользователя."""
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

    response = await client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["username"] == "testuser"


@pytest.mark.asyncio
async def test_get_me_unauthorized(client: AsyncClient):
    """Тест запроса /me без токена."""
    response = await client.get("/auth/me")
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_auth_register_login_me(client: AsyncClient):
    """Сценарий регистрации, входа и запроса текущего пользователя."""
    response = await client.post(
        "/auth/register",
        json={
            "email": "user@example.com",
            "username": "user",
            "password": "password123",
        },
    )
    assert response.status_code == 200

    login_response = await client.post(
        "/auth/login",
        json={
            "email": "user@example.com",
            "password": "password123",
        },
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    me_response = await client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert me_response.status_code == 200
    me_data = me_response.json()
    assert me_data["email"] == "user@example.com"
