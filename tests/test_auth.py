from sqlalchemy import select

from apps.users.models import UserSettings
from tests.conftest import auth_headers, login_user, register_user


async def test_register_creates_user_and_settings(client, db_session, user_payload):
    response = await register_user(client, user_payload)

    assert response.status_code == 201
    body = response.json()
    assert body["username"] == "owner"
    assert "password" not in body
    assert "password_hash" not in body

    settings = await db_session.scalar(select(UserSettings))
    assert settings is not None
    assert settings.individual_pd is True
    assert settings.individual_add is True


async def test_duplicate_username_is_rejected(client, user_payload):
    assert (await register_user(client, user_payload)).status_code == 201

    duplicate = {**user_payload, "email": "another@example.com"}
    response = await register_user(client, duplicate)

    assert response.status_code == 409


async def test_username_login_and_current_user(client, user_payload):
    await register_user(client, user_payload)
    token = await login_user(client, "owner", "password123")

    response = await client.get("/auth/me", headers=auth_headers(token))

    assert response.status_code == 200
    assert response.json()["username"] == "owner"


async def test_invalid_login_is_rejected(client, user_payload):
    await register_user(client, user_payload)

    response = await client.post(
        "/auth/token",
        data={"username": "owner", "password": "wrong-password"},
    )

    assert response.status_code == 401


async def test_protected_endpoint_requires_authentication(client):
    response = await client.get("/patients")

    assert response.status_code == 401
