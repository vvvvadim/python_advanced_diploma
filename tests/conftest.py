import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from fastapi.testclient import TestClient

from api.database.database import Base, get_async_session
from api.config.models import User
from api.config.config import TEST_DATABASE_URL
from api.main import app

# Создаем асинхронный движок для тестовой базы данных
engine = create_async_engine(TEST_DATABASE_URL, echo=True)

# Создаем фабрику сессий
async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

@pytest_asyncio.fixture(scope="function")
async def setup_database():
    """Create a fresh database for each test."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    async with async_session() as session:
        # Создаем тестового пользователя
        user = User(
            name="Test User",
            api_key="test"
        )
        session.add(user)
        
        # Создаем второго тестового пользователя
        user2 = User(
            name="Test User 2",
            api_key="test2"
        )
        session.add(user2)
        
        await session.commit()
        await session.refresh(user)
        await session.refresh(user2)
        print(f"Created test user with id: {user.id}, api_key: {user.api_key}")
        print(f"Created test user 2 with id: {user2.id}, api_key: {user2.api_key}")
    
    yield
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()

@pytest_asyncio.fixture(scope="function")
async def session(setup_database) -> AsyncSession:
    """Create a fresh database session for each test."""
    async with async_session() as session:
        yield session
        await session.rollback()
        await session.close()

@pytest_asyncio.fixture(scope="function")
async def test_user(session: AsyncSession) -> User:
    """Get the test user."""
    result = await session.execute(select(User).where(User.api_key == "test"))
    user = result.scalar_one_or_none()
    if user:
        print(f"Found test user with id: {user.id}, api_key: {user.api_key}")
    else:
        print("Test user not found!")
    return user

@pytest_asyncio.fixture(scope="function")
async def test_user2(session: AsyncSession) -> User:
    """Get the second test user."""
    result = await session.execute(select(User).where(User.api_key == "test2"))
    user = result.scalar_one_or_none()
    if user:
        print(f"Found test user 2 with id: {user.id}, api_key: {user.api_key}")
    else:
        print("Test user 2 not found!")
    return user

@pytest.fixture(scope="function")
def client(session: AsyncSession):
    """Create a test client that uses the test database."""
    app.dependency_overrides = {}  # Сбрасываем все переопределения зависимостей
    app.dependency_overrides[get_async_session] = lambda: session
    return TestClient(app) 