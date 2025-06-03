from collections.abc import AsyncGenerator
from typing import Dict, Mapping

import pytest
import pytest_asyncio
from api.database.database import Base, get_async_session
from fastapi import FastAPI
from httpx import AsyncClient
from api.main import app
from api.config.models import User
from api.config.config import settings
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

# DB_USERNAME = "test"
# DB_PASSWORD = "test"
# DB_HOST = "localhost"
# DB_PORT = 5432
# DB_NAME = "test_db"

TEST_USERNAME = "Test"
TEST_API_KEY = "test"
TEST_SERVER_PORT = 8000

unauthorized_structure_response: Dict = {
    "result": False,
    "error_type": "Unauthorized",
    "error_message": "Неверный API ключ",
}


@pytest_asyncio.fixture()
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    # DATABASE_URL = f"postgresql+asyncpg://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    DATABASE_URL = settings.get_db_url()
    engine = create_async_engine(DATABASE_URL, echo=True)
    async_session = async_sessionmaker(engine, expire_on_commit=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    async with async_session() as session:
        test_user = User(api_key=TEST_API_KEY, name=TEST_USERNAME)
        session.add(test_user)
        fake_users = [
            User(api_key=f"fake_api_key{i}", name=f"fake_user{i}")
            for i in range(1, 6)
        ]
        session.add_all(fake_users)
        yield session
        await session.close()


@pytest.fixture()
def test_app(db_session: AsyncSession) -> FastAPI:
    """Create a test app with overridden dependencies."""
    app.dependency_overrides[get_async_session] = lambda: db_session
    return app


@pytest_asyncio.fixture()
async def client(test_app: FastAPI) -> AsyncGenerator[AsyncClient, None]:
    """Create a http client."""
    test_headers: Mapping[str, str] = {"api-key": "unauthorized"}
    if TEST_API_KEY is not None:
        test_headers = {"api-key": TEST_API_KEY}
    async with AsyncClient(
        app=test_app,
        base_url=f"http://localhost:{TEST_SERVER_PORT}/api",
        headers=test_headers,
    ) as client:
        yield client


@pytest_asyncio.fixture()
async def invalid_client(
    test_app: FastAPI,
) -> AsyncGenerator[AsyncClient, None]:
    test_headers: Mapping[str, str] = {"api-key": "unauthorized"}
    async with AsyncClient(
        app=test_app,
        base_url=f"http://localhost:{TEST_SERVER_PORT}/api",
        headers=test_headers,
    ) as client:
        yield client