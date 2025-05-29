import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from fastapi.security import APIKeyHeader
from pathlib import Path


class Settings(BaseSettings):
    DB_USERNAME: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str

    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    )

    def get_db_url(self):
        return (f"postgresql+asyncpg://{self.DB_USERNAME}:{self.DB_PASSWORD}@"
                f"{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}")


class TestSettings(BaseSettings):
    DB_USERNAME: str = "test_user"
    DB_PASSWORD: str = "test_password"
    DB_HOST: str = "localhost"
    DB_PORT: int = 5434
    DB_NAME: str = "twitter_test"

    def get_db_url(self):
        return (f"postgresql+asyncpg://{self.DB_USERNAME}:{self.DB_PASSWORD}@"
                f"{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}")


settings = Settings()
test_settings = TestSettings()

API_KEY_HEADER = APIKeyHeader(name="api-key")

# Базовые настройки
BASE_DIR = Path(__file__).resolve().parent.parent
MEDIA_FOLDER = os.path.join(BASE_DIR, "media")

# Настройки базы данных
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

# Создаем папку для медиафайлов, если она не существует
os.makedirs(MEDIA_FOLDER, exist_ok=True)
