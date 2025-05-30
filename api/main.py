from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError, ResponseValidationError
from starlette.exceptions import HTTPException

from api.config.exceptions import (Error_DB, all_http_exception_handler,
                                   custom_exception_handler,
                                   response_validation_exception_handler,
                                   validation_exception_handler)
from api.database.database import Base, engine
from api.routers import media, tweets, users


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("База готова")
    yield
    await engine.dispose()
    print("Работа приложения завершена")


app = FastAPI(lifespan=lifespan, debug=True)

app.add_exception_handler(Error_DB, custom_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(HTTPException, all_http_exception_handler)
app.add_exception_handler(
    ResponseValidationError, response_validation_exception_handler
)

app.include_router(users.user_router)
app.include_router(tweets.tweets_router)
app.include_router(media.media_router)
