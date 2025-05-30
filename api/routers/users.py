from fastapi import APIRouter, Depends, status

from api.config.models import User
from api.config.schemas import MSG, GetUser
from api.function.user_func import (get_user_by_id, get_user_by_token,
                                    user_follow, user_unfollow)

user_router = APIRouter(tags=["Работа с пользователями"])


@user_router.get(
    "/api/users/me",
    status_code=status.HTTP_200_OK,
    response_model=GetUser,
    description="Получение информации о своём профиле",
    name="Получение информации о своём профиле по API-ключу",
)
async def get_users_me(current_user: User = Depends(get_user_by_token)):
    return {"result": True, "user": current_user}


@user_router.get(
    "/api/users/{user_id}",
    status_code=status.HTTP_200_OK,
    response_model=GetUser,
    name="Получение информации о произвольном профиле по его id",
    description="Получение информации о произвольном профиле по его id",
)
async def get_users(current_user: User = Depends(get_user_by_id)):
    return {"result": True, "user": current_user}


@user_router.post(
    "/api/users/{user_id}/follow",
    status_code=status.HTTP_200_OK,
    response_model=MSG,
    name="Подписка на пользователя",
    description="Подписка на пользователя по его id",
)
async def follow_users(result: MSG = Depends(user_follow)):
    return result


@user_router.delete(
    "/api/users/{user_id}/follow",
    status_code=status.HTTP_200_OK,
    response_model=MSG,
    name="Отписка от пользователя",
    description="Отписка от пользователя по его id",
)
async def unfollow_users(result: MSG = Depends(user_unfollow)):
    return result
