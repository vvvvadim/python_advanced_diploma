from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse

main_router = APIRouter(tags=["Главная страница"])


@main_router.get("/", name="Переадресация на главную страницу")
async def main_func(request: Request):
    return RedirectResponse(url="http://localhost", status_code=301)
