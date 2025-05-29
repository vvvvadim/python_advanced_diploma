from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased,selectinload
from sqlalchemy import select, delete
from typing import List
from fastapi import HTTPException, Depends,status
import os

from api.database.database import get_async_session
from api.function.user_func import get_user_by_token
from api.config.models import Tweet, Like, User, Media
from api.config.schemas import TweetPost, Tweets,UserSCH
from api.config.config import MEDIA_FOLDER


async def get_tweet_func(user: UserSCH = Depends(get_user_by_token),
                         session: AsyncSession = Depends(get_async_session)
                         ) -> List[Tweets]:
    """Получение твитов пользователя и его подписок"""
    following_ids = [following.id for following in user.following]
    following_ids.append(user.id)

    author = aliased(User, name='author')
    liker = aliased(User, name='liker')

    stmt = (
        select(
            Tweet.id,
            Tweet.content,
            author.id.label('author_id'),
            author.name.label('author_name'),
            Media.link.label('media_link'),
            Like.user_id.label('like_user_id'),
            liker.name.label('like_user_name')
        )
        .join(author, Tweet.author)
        .outerjoin(Tweet.attachments)
        .outerjoin(Tweet.likes)
        .outerjoin(liker, Like.users_lk)
        .filter(Tweet.author_id.in_(following_ids))
        .order_by(Tweet.created_at.desc())
    )

    result = await session.execute(stmt)

    # Группируем результаты по твитам
    tweets_dict = {}
    for row in result.all():
        if row.id not in tweets_dict:
            tweets_dict[row.id] = {
                'id': row.id,
                'content': row.content,
                'attachments': [],
                'author': {
                    'id': row.author_id,
                    'name': row.author_name
                },
                'likes': []
            }

        # Добавляем attachment, если есть
        if row.media_link:
            attachment = row.media_link
            if attachment not in tweets_dict[row.id]['attachments']:
                tweets_dict[row.id]['attachments'].append(attachment)

        # Добавляем like, если есть
        if row.like_user_id and not any(like['user_id'] == row.like_user_id for like in tweets_dict[row.id]['likes']):
            tweets_dict[row.id]['likes'].append({
                'user_id': row.like_user_id,
                'name': row.like_user_name
            })

    return list(tweets_dict.values())


async def post_tweet_func(tweet_post: TweetPost,
                          user: UserSCH = Depends(get_user_by_token),
                          session: AsyncSession = Depends(get_async_session)
                          ) -> dict:
    """Создание нового твита"""
    tweet = Tweet(content=tweet_post.tweet_data, author_id=user.id)
    session.add(tweet)
    await session.flush()

    if tweet_post.tweet_media_ids:
        # Привязываем медиафайлы к твиту
        result = await session.execute(
            select(Media).where(Media.id.in_(tweet_post.tweet_media_ids))
        )
        media_files = result.scalars().all()

        if len(media_files) != len(tweet_post.tweet_media_ids):
            raise HTTPException(
                status_code=500,
                detail="Некоторые медиафайлы не найдены"
            )

        for media in media_files:
            media.tweet_id = tweet.id

    return {"result": "true", "tweet_id": tweet.id}


async def delete_tweet(tweet_id: int,
                       current_user: UserSCH = Depends(get_user_by_token),
                       session: AsyncSession = Depends(get_async_session)
                       ) -> dict:
    """Зависимость для проверки владения твитом"""
    query = (select(Tweet)
             .where(
         Tweet.id == tweet_id,
                     Tweet.author_id == current_user.id
                     )
         .options(
        selectinload(Tweet.attachments)
    )
    )
    result = await session.execute(query)
    tweet = result.scalar_one_or_none()

    if not tweet:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="У вас нет прав на выполнение этой операции"
        )
    else:
        for file in tweet.attachments:
            file_link = os.path.join(MEDIA_FOLDER, file.link)
            os.remove(file_link)
        await session.delete(tweet)
        return {"result": True}


async def set_like_tweet(tweet_id: int,
                         user: UserSCH = Depends(get_user_by_token),
                         session: AsyncSession = Depends(get_async_session)
                         ) -> dict:
    """Поставить лайк твиту"""
    # Проверяем существование твита
    result = await session.execute(
        select(Tweet).where(Tweet.id == tweet_id)
    )
    tweet = result.scalar_one_or_none()
    
    if tweet is None:
        raise HTTPException(
            status_code=500,
            detail="Твит не найден"
        )
    
    # Проверяем, не стоит ли уже лайк
    result = await session.execute(
        select(Like)
        .where(Like.tweet_id == tweet_id)
        .where(Like.user_id == user.id)
    )
    if result.scalar_one_or_none() is not None:
        raise HTTPException(
            status_code=500,
            detail="Вы уже поставили лайк этому твиту"
        )

    # Создаем новый лайк
    like = Like(user_id=user.id, tweet_id=tweet_id)
    session.add(like)
    return {"result": "true"}


async def del_like_tweet(tweet_id: int,
                         user: UserSCH = Depends(get_user_by_token),
                         session: AsyncSession = Depends(get_async_session)
                         ) -> dict:
    """Удалить лайк с твита"""
    result = await session.execute(
        delete(Like)
        .where(Like.tweet_id == tweet_id)
        .where(Like.user_id == user.id)
        .returning(Like.id)
    )
    if result.scalar_one_or_none() is None:
        raise HTTPException(
            status_code=500,
            detail="Лайк не найден"
        )
    
    return {"result": "true"}

