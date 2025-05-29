from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, PrivateAttr, ConfigDict


class Follow(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)


class UserSCH(BaseModel):
    id: int
    name: str
    followers: Optional[List[Follow]] = None
    following: Optional[List[Follow]] = None
    _api_key: str = PrivateAttr()
    _created_at: datetime = PrivateAttr()
    _updated_at: datetime = PrivateAttr()

    model_config = ConfigDict(from_attributes=True)


class GetUser(BaseModel):
    result: bool
    user: UserSCH

    model_config = ConfigDict(from_attributes=True)


class ErrorMSG(BaseModel):
    result: bool = False
    error_type: str
    error_message: str

    model_config = ConfigDict(from_attributes=True)


class MSG(BaseModel):
    result: bool = True

    model_config = ConfigDict(from_attributes=True)


class TweetPost(BaseModel):
    tweet_data: str
    tweet_media_ids: Optional[List[int]] = None

    model_config = ConfigDict(from_attributes=True)


class TweetResp(BaseModel):
    result: bool = True
    tweet_id: int

    model_config = ConfigDict(from_attributes=True)


class Likes(BaseModel):
    user_id: int
    name: str

    model_config = ConfigDict(from_attributes=True)

class Media(BaseModel):
    link : str

    model_config = ConfigDict(from_attributes=True)

class TweetAuthor(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)


class Tweets(BaseModel):
    id: int
    content: str
    author: TweetAuthor
    attachments: Optional[List] = None
    likes: Optional[List[Likes]] = None

    model_config = ConfigDict(from_attributes=True)


class GetTweet(BaseModel):
    result: bool
    tweets: List[Tweets]

    model_config = ConfigDict(from_attributes=True)