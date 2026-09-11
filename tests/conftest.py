import os
from collections.abc import AsyncGenerator

import httpx
import pytest
import pytest_asyncio
from sqlalchemy import make_url, text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from core.database import Base
from core.database.dependencies import get_session
from main import app


@pytest.fixture(scope="session")
def test_database_url() -> str:
    database_url = os.getenv("TEST_DATABASE_URL")
    if not database_url:
        pytest.fail(
            "TEST_DATABASE_URL must point to a dedicated PostgreSQL test database"
        )
    if not database_url.startswith("postgresql+psycopg://"):
        pytest.fail("TEST_DATABASE_URL must use postgresql+psycopg://")
    if "test" not in (make_url(database_url).database or "").lower():
        pytest.fail("TEST_DATABASE_URL must point to a database whose name contains 'test'")
    return database_url


@pytest_asyncio.fixture(scope="session")
async def test_engine(test_database_url: str) -> AsyncGenerator[AsyncEngine, None]:
    engine = create_async_engine(test_database_url, pool_pre_ping=True)
    try:
        async with engine.begin() as connection:
            await connection.execute(text("CREATE EXTENSION IF NOT EXISTS citext"))
            await connection.run_sync(Base.metadata.drop_all)
            await connection.run_sync(Base.metadata.create_all)
        yield engine
    finally:
        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.drop_all)
        await engine.dispose()


@pytest_asyncio.fixture
async def clean_database(test_engine: AsyncEngine) -> AsyncGenerator[None, None]:
    async with test_engine.begin() as connection:
        await connection.execute(
            text(
                "TRUNCATE TABLE prescriptions, user_settings, patients, users "
                "RESTART IDENTITY CASCADE"
            )
        )
    yield


@pytest_asyncio.fixture
async def db_session(test_engine: AsyncEngine) -> AsyncGenerator[AsyncSession, None]:
    session_factory = async_sessionmaker(test_engine, expire_on_commit=False)
    async with session_factory() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture
async def client(
    test_engine: AsyncEngine,
    clean_database: None,
) -> AsyncGenerator[httpx.AsyncClient, None]:
    session_factory = async_sessionmaker(test_engine, expire_on_commit=False)

    async def override_session() -> AsyncGenerator[AsyncSession, None]:
        async with session_factory() as session:
            yield session

    app.dependency_overrides[get_session] = override_session
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as test_client:
        yield test_client
    app.dependency_overrides.pop(get_session, None)


@pytest.fixture
def user_payload() -> dict[str, str]:
    return {
        "username": "owner",
        "email": "owner@example.com",
        "password": "password123",
        "repeat_password": "password123",
    }


async def register_user(
    client: httpx.AsyncClient,
    payload: dict[str, str],
) -> httpx.Response:
    return await client.post("/auth/register", json=payload)


async def login_user(client: httpx.AsyncClient, username: str, password: str) -> str:
    response = await client.post(
        "/auth/token",
        data={"username": username, "password": password},
    )
    response.raise_for_status()
    return response.json()["access_token"]


def auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}
