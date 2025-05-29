import pytest
from fastapi.testclient import TestClient
from api.main import app
from sqlalchemy.ext.asyncio import AsyncSession
from api.config.models import User, Tweet, Like, Media
from sqlalchemy import select
import pytest_asyncio
from api.database.database import get_async_session
import os
from api.config.config import MEDIA_FOLDER

client = TestClient(app)

@pytest_asyncio.fixture(autouse=True)
async def override_dependency(session: AsyncSession):
    """Override the database session dependency for tests."""
    app.dependency_overrides[get_async_session] = lambda: session
    yield
    app.dependency_overrides.clear()

@pytest_asyncio.fixture
async def test_token(session: AsyncSession):
    # Создаем тестового пользователя, если его нет
    result = await session.execute(select(User).where(User.api_key == "test"))
    user = result.scalar_one_or_none()
    
    if not user:
        user = User(name="Test User", api_key="test")
        session.add(user)
        await session.commit()
        await session.refresh(user)
        print(f"Created test user in test_token fixture with id: {user.id}, api_key: {user.api_key}")
    else:
        print(f"Found test user in test_token fixture with id: {user.id}, api_key: {user.api_key}")
    
    return user.api_key

@pytest_asyncio.fixture
async def test_user_id(session: AsyncSession):
    # Создаем тестового пользователя, если его нет
    result = await session.execute(select(User).where(User.api_key == "test"))
    user = result.scalar_one_or_none()
    
    if not user:
        user = User(name="Test User", api_key="test")
        session.add(user)
        await session.commit()
        await session.refresh(user)
        print(f"Created test user in test_user_id fixture with id: {user.id}, api_key: {user.api_key}")
    else:
        print(f"Found test user in test_user_id fixture with id: {user.id}, api_key: {user.api_key}")
    
    return user.id

@pytest_asyncio.fixture
async def test_tweet_id(session: AsyncSession, test_user_id):
    # Создаем тестовый твит
    tweet = Tweet(content="Test tweet", author_id=test_user_id)
    session.add(tweet)
    await session.commit()
    await session.refresh(tweet)
    print(f"Created test tweet with id: {tweet.id}, author_id: {tweet.author_id}")
    return tweet.id

@pytest_asyncio.fixture
async def test_like(session: AsyncSession, test_user_id, test_tweet_id):
    # Создаем тестовый лайк
    like = Like(user_id=test_user_id, tweet_id=test_tweet_id)
    session.add(like)
    await session.commit()
    await session.refresh(like)
    print(f"Created test like with id: {like.id}, user_id: {like.user_id}, tweet_id: {like.tweet_id}")
    return like.id

@pytest.fixture
def test_tweet_data():
    return {
        "tweet_data": "Test tweet",
        "tweet_media_ids": []
    }

@pytest.fixture
def test_media_file():
    """Создает тестовый медиафайл"""
    test_file_path = "test_image.jpg"
    with open(test_file_path, "wb") as f:
        f.write(b"test image content")
    yield test_file_path
    # Удаляем тестовый файл после теста
    if os.path.exists(test_file_path):
        os.remove(test_file_path)

# Тесты для пользователей
@pytest.mark.asyncio
async def test_get_users_me(test_token, client):
    print(f"Testing get_users_me with token: {test_token}")
    response = client.get("/api/users/me", headers={"api-key": test_token})
    print(f"Response status: {response.status_code}, body: {response.json()}")
    assert response.status_code == 200
    assert "result" in response.json()
    assert "user" in response.json()

@pytest.mark.asyncio
async def test_get_users(test_user_id, client):
    print(f"Testing get_users with user_id: {test_user_id}")
    response = client.get(f"/api/users/{test_user_id}")
    print(f"Response status: {response.status_code}, body: {response.json()}")
    assert response.status_code == 200
    assert "result" in response.json()
    assert "user" in response.json()

@pytest.mark.asyncio
async def test_follow_and_unfollow_users(test_token, test_user2, client):
    # Сначала подписываемся
    print(f"Testing follow_users with token: {test_token}, user_id: {test_user2.id}")
    follow_response = client.post(
        f"/api/users/{test_user2.id}/follow",
        headers={"api-key": test_token}
    )
    print(f"Follow response status: {follow_response.status_code}, body: {follow_response.json()}")
    assert follow_response.status_code == 200
    assert "result" in follow_response.json()

    # Затем отписываемся
    print(f"Testing unfollow_users with token: {test_token}, user_id: {test_user2.id}")
    unfollow_response = client.delete(
        f"/api/users/{test_user2.id}/follow",
        headers={"api-key": test_token}
    )
    print(f"Unfollow response status: {unfollow_response.status_code}, body: {unfollow_response.json()}")
    assert unfollow_response.status_code == 200
    assert "result" in unfollow_response.json()

# Тесты для медиафайлов
@pytest.mark.asyncio
async def test_media_upload(test_token, test_media_file, client, session):
    """Тест загрузки медиафайла"""
    print(f"Testing media upload with file: {test_media_file}")
    with open(test_media_file, "rb") as f:
        upload_response = client.post(
            "/api/medias",
            headers={"api-key": test_token},
            files={"file": ("test_image.jpg", f, "image/jpeg")}
        )
    print(f"Upload response status: {upload_response.status_code}")
    print(f"Upload response body: {upload_response.json()}")
    assert upload_response.status_code == 200
    response_data = upload_response.json()
    print(f"Response data type: {type(response_data)}")
    print(f"Response data: {response_data}")
    assert "result" in response_data
    assert response_data["result"] == "true"
    assert "media_id" in response_data
    media_id = response_data["media_id"]
    print(f"Media ID: {media_id}")

    # Проверяем имя файла в базе данных
    result = await session.execute(select(Media).where(Media.id == media_id))
    media = result.scalar_one_or_none()
    assert media is not None
    print(f"Media link in database: {media.link}")

    # Проверяем размер файла
    media_path = os.path.join(MEDIA_FOLDER, media.link)
    assert os.path.exists(media_path)
    original_size = os.path.getsize(test_media_file)
    uploaded_size = os.path.getsize(media_path)
    print(f"Original file size: {original_size}, Uploaded file size: {uploaded_size}")
    assert uploaded_size > 0

    return media_id, media_path

@pytest.mark.asyncio
async def test_tweet_with_media(test_token, test_media_file, client, session):
    """Тест создания твита с медиафайлом"""
    # Сначала загружаем медиафайл
    media_id, media_path = await test_media_upload(test_token, test_media_file, client, session)

    # Создаем твит с прикрепленным медиафайлом
    tweet_data = {
        "tweet_data": "Test tweet with media",
        "tweet_media_ids": [media_id]
    }
    print(f"Testing tweet creation with media_id: {media_id}")
    tweet_response = client.post(
        "/api/tweets",
        headers={"api-key": test_token},
        json=tweet_data
    )
    print(f"Tweet response status: {tweet_response.status_code}")
    print(f"Tweet response body: {tweet_response.json()}")
    assert tweet_response.status_code == 200
    tweet_data = tweet_response.json()
    print(f"Tweet data type: {type(tweet_data)}")
    print(f"Tweet data: {tweet_data}")
    assert "result" in tweet_data
    assert tweet_data["result"] is True
    assert "tweet_id" in tweet_data
    tweet_id = tweet_data["tweet_id"]
    print(f"Tweet ID: {tweet_id}")

    return tweet_id, media_path

@pytest.mark.asyncio
async def test_tweet_likes(test_token, test_media_file, client, session):
    """Тест лайков твита"""
    # Создаем твит с медиафайлом
    tweet_id, _ = await test_tweet_with_media(test_token, test_media_file, client, session)

    # Ставим лайк
    like_response = client.post(
        f"/api/tweets/{tweet_id}/likes",
        headers={"api-key": test_token}
    )
    print(f"Like response status: {like_response.status_code}")
    print(f"Like response body: {like_response.json()}")
    assert like_response.status_code == 200
    like_data = like_response.json()
    print(f"Like data type: {type(like_data)}")
    print(f"Like data: {like_data}")
    assert "result" in like_data
    assert like_data["result"] is True

    # Удаляем лайк
    unlike_response = client.delete(
        f"/api/tweets/{tweet_id}/likes",
        headers={"api-key": test_token}
    )
    print(f"Unlike response status: {unlike_response.status_code}")
    print(f"Unlike response body: {unlike_response.json()}")
    assert unlike_response.status_code == 200
    unlike_data = unlike_response.json()
    print(f"Unlike data type: {type(unlike_data)}")
    print(f"Unlike data: {unlike_data}")
    assert "result" in unlike_data
    assert unlike_data["result"] is True

    return tweet_id

@pytest.mark.asyncio
async def test_tweet_delete(test_token, test_media_file, client, session):
    """Тест удаления твита"""
    # Создаем твит с медиафайлом
    tweet_id, media_path = await test_tweet_with_media(test_token, test_media_file, client, session)

    # Удаляем твит
    delete_response = client.delete(
        f"/api/tweets/{tweet_id}",
        headers={"api-key": test_token}
    )
    print(f"Delete tweet response status: {delete_response.status_code}")
    print(f"Delete tweet response body: {delete_response.json()}")
    assert delete_response.status_code == 200
    delete_data = delete_response.json()
    print(f"Delete data type: {type(delete_data)}")
    print(f"Delete data: {delete_data}")
    assert "result" in delete_data
    assert delete_data["result"] is True

    # Проверяем, что файл удален
    assert not os.path.exists(media_path)

@pytest.mark.asyncio
async def test_media_upload_and_tweet(test_token, test_media_file, client, session):
    """Полный тест загрузки медиафайла, создания твита, лайков и удаления"""
    # Загружаем медиафайл и создаем твит
    tweet_id, media_path = await test_tweet_with_media(test_token, test_media_file, client, session)

    # Тестируем лайки
    await test_tweet_likes(test_token, test_media_file, client, session)

    # Удаляем твит и проверяем удаление файла
    await test_tweet_delete(test_token, test_media_file, client, session)

# Тесты для твитов
@pytest.mark.asyncio
async def test_get_tweets(test_token, client):
    print(f"Testing get_tweets with token: {test_token}")
    response = client.get("/api/tweets", headers={"api-key": test_token})
    print(f"Response status: {response.status_code}, body: {response.json()}")
    assert response.status_code == 200
    assert "result" in response.json()
    assert "tweets" in response.json()