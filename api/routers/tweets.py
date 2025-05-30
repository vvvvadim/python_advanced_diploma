from typing import List

from fastapi import APIRouter, Depends, status

from api.config.models import Tweet
from api.config.schemas import MSG, GetTweet, TweetResp
from api.function.tweet_func import (del_like_tweet, delete_tweet,
                                     get_tweet_func, post_tweet_func,
                                     set_like_tweet)

tweets_router = APIRouter(tags=["Работа с твитами"])


@tweets_router.get(
    "/api/tweets",
    status_code=status.HTTP_200_OK,
    response_model=GetTweet,
    name="Получение ленты с твитами",
    description="Получение ленты с твитами пользователя по API-ключу",
)
async def get_tweet(tweets: List[Tweet] = Depends(get_tweet_func)):
    return {"result": "true", "tweets": tweets}


@tweets_router.post(
    "/api/tweets",
    status_code=status.HTTP_200_OK,
    response_model=TweetResp,
    name="Создание твита",
    description="Создание твита по API-ключу",
)
async def post_tweet(result: dict = Depends(post_tweet_func)):
    return result


@tweets_router.delete(
    "/api/tweets/{tweet_id}",
    status_code=status.HTTP_200_OK,
    response_model=MSG,
    name="Удаление твита",
    description="Удаление твита по id и API-ключу",
)
async def delete_tweets(result: MSG = Depends(delete_tweet)):
    return result


@tweets_router.post(
    "/api/tweets/{tweet_id}/likes",
    status_code=status.HTTP_200_OK,
    response_model=MSG,
    name="Установка отметки «Нравится» на твит",
    description="Установка отметки «Нравится» на твит по id твита и API-ключу",
)
async def post_like_tweet(result: MSG = Depends(set_like_tweet)):
    return result


@tweets_router.delete(
    "/api/tweets/{tweet_id}/likes",
    status_code=status.HTTP_200_OK,
    response_model=MSG,
    name="Удаление отметки «Нравится» с твита",
    description="Удаление отметки «Нравится» с твита по id твита и API-ключу",
)
async def delete_like_tweet(result: MSG = Depends(del_like_tweet)):
    return result
