import logging
import os

from fastapi.security import APIKeyHeader
from pydantic_settings import BaseSettings, SettingsConfigDict


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
        return (
            f"postgresql+asyncpg://{self.DB_USERNAME}:{self.DB_PASSWORD}@"
            f"{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )


def setup_logger():
    logger = logging.getLogger("TWITTER-BACKEND")
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger


logger = setup_logger()

settings = Settings()

API_KEY_HEADER = APIKeyHeader(name="api-key")

MEDIA_FOLDER = os.path.join("/media")


# logger = logging.getLogger(__name__)
#
# logging.basicConfig(
#     level=logging.INFO,
#     format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
# )
#
#
# def create_route_logger(route_name: str):
#     def get_route_logger():
#         logger = logging.getLogger(f"app.{route_name}")
#
#         class RouteFilter(logging.Filter):
#             def filter(self, record):
#                 record.route = route_name
#                 return True
#
#         if not any(isinstance(f, RouteFilter) for f in logger.filters):
#             logger.addFilter(RouteFilter())
#
#         return logger
#
#     return get_route_logger
