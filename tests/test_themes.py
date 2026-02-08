
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.user import User


async def create_user(client: AsyncClient, email: str, username: str) -> tuple[str, str]:
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


async def promote_admin(db_session: AsyncSession, user_id: str) -> None:
    result = await db_session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one()
    user.is_admin = True
    await db_session.commit()
    await db_session.refresh(user)


@pytest.mark.asyncio
async def test_themes_admin_crud(client: AsyncClient, db_session: AsyncSession):
    token, user_id = await create_user(client, "admin_theme@example.com", "admin_theme")
    await promote_admin(db_session, user_id)

    create_resp = await client.post(
        "/themes",
        headers={"Authorization": f"Bearer {token}"},
        json={"name": "Backend", "description": "Backend tasks"},
    )
    assert create_resp.status_code == 200
    theme_id = create_resp.json()["id"]

    list_resp = await client.get("/themes")
    assert list_resp.status_code == 200
    assert any(item["id"] == theme_id for item in list_resp.json())

    patch_resp = await client.patch(
        f"/themes/{theme_id}",
        headers={"Authorization": f"Bearer {token}"},
        json={"name": "Backend Updated"},
    )
    assert patch_resp.status_code == 200
    assert patch_resp.json()["name"] == "Backend Updated"

    delete_resp = await client.delete(
        f"/themes/{theme_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert delete_resp.status_code == 204


@pytest.mark.asyncio
async def test_themes_non_admin_forbidden(client: AsyncClient):
    token, _ = await create_user(client, "user_theme@example.com", "user_theme")
    response = await client.post(
        "/themes",
        headers={"Authorization": f"Bearer {token}"},
        json={"name": "NoAdmin", "description": "Should fail"},
    )
    assert response.status_code == 403
