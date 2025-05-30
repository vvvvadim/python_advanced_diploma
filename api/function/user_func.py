from typing import Dict

from fastapi import Depends, HTTPException, status
from sqlalchemy import delete, select
from sqlalchemy.dialects.mysql import insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from api.config.config import API_KEY_HEADER
from api.config.models import User, follower_tbl
from api.database.database import get_async_session


async def get_user_by_token(
    token: str = Depends(API_KEY_HEADER),
    session: AsyncSession = Depends(get_async_session),
) -> User:
    """Зависимость для получения текущего пользователя по API ключу"""
    query = (
        select(User)
        .where(User.api_key == token)
        .options(selectinload(User.following), selectinload(User.followers))
    )
    result = await session.execute(query)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Неверный API ключ"
        )
    return user


async def get_user_by_id(
    user_id: int, session: AsyncSession = Depends(get_async_session)
) -> User:
    """Получение пользователя по ID или токену"""
    query = (
        select(User)
        .where(User.id == user_id)
        .options(selectinload(User.following), selectinload(User.followers))
    )
    result = await session.execute(query)
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Пользователь не найден"
        )
    return user


async def user_follow(
    user_id: int,
    follower: User = Depends(get_user_by_token),
    session: AsyncSession = Depends(get_async_session),
) -> Dict:
    """Подписка на пользователя"""
    if await check_user_follow(
        session=session, follower_id=follower.id, following_id=user_id
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Вы уже подписаны на этого пользователя",
        )
    else:
        await session.execute(
            insert(follower_tbl).values(follower_id=follower.id, following_id=user_id)
        )
        await session.commit()
        return {"result": "true"}


async def user_unfollow(
    user_id: int,
    follower: User = Depends(get_user_by_token),
    session: AsyncSession = Depends(get_async_session),
) -> Dict:
    """Отписка от пользователя"""
    if not await check_user_follow(
        session=session, follower_id=follower.id, following_id=user_id
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Вы не подписаны на этого пользователя",
        )
    else:
        await session.execute(
            delete(follower_tbl).where(
                follower_tbl.c.follower_id == follower.id,
                follower_tbl.c.following_id == user_id,
            )
        )
        await session.commit()
        return {"result": "true"}


async def check_user_follow(
    follower_id: int,
    following_id: int,
    session: AsyncSession = Depends(get_async_session),
) -> bool:
    """Проверка подписки на пользователя"""
    if follower_id == following_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Нельзя подписаться на самого себя",
        )
    else:
        result = await session.execute(
            select(follower_tbl).filter_by(
                follower_id=follower_id, following_id=following_id
            )
        )
        result = result.scalar_one_or_none()
        if result is None:
            return False
        else:
            return True
