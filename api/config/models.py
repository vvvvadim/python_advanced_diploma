from typing import List

from sqlalchemy import (TIMESTAMP, Column, ForeignKey, Integer, String, Table,
                        func)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from api.database.database import Base, uniq_str_an

follower_tbl = Table(
    "followers_tbl",
    Base.metadata,
    Column("follower_id", Integer, ForeignKey("users.id"), primary_key=True),
    Column("following_id", Integer, ForeignKey("users.id"), primary_key=True),
    Column("created_at", TIMESTAMP(timezone=True), server_default=func.now()),
    Column(
        "updated_at",
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    ),
)


class User(Base):
    name: Mapped[str] = mapped_column(nullable=False, index=True)
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, index=True)
    api_key: Mapped[uniq_str_an]
    followers: Mapped[list["User"]] = relationship(
        "User",
        secondary=follower_tbl,
        primaryjoin=(follower_tbl.c.following_id == id),
        secondaryjoin=(follower_tbl.c.follower_id == id),
        back_populates="following",
        lazy="selectin",
    )
    following: Mapped[list["User"]] = relationship(
        "User",
        secondary=follower_tbl,
        primaryjoin=(follower_tbl.c.follower_id == id),
        secondaryjoin=(follower_tbl.c.following_id == id),
        back_populates="followers",
        lazy="selectin",
    )
    likes = relationship(
        "Like", back_populates="users_lk", cascade="all, delete-orphan"
    )
    tweets = relationship(
        "Tweet", back_populates="author", cascade="all, delete-orphan"
    )

    __mapper_args__ = {"confirm_deleted_rows": False}


class Tweet(Base):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, index=True)
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    content: Mapped[str] = mapped_column(String(2500))
    attachments: Mapped[List["Media"]] = relationship(
        backref="tweets", cascade="all, delete-orphan"
    )
    likes: Mapped[List["Like"]] = relationship(
        backref="tweets", cascade="all, delete-orphan"
    )
    author: Mapped["User"] = relationship(
        "User", back_populates="tweets", lazy="selectin", innerjoin=True
    )


class Like(Base):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    tweet_id: Mapped[int] = mapped_column(ForeignKey("tweets.id"), nullable=False)

    users_lk: Mapped["User"] = relationship(
        "User", back_populates="likes", lazy="joined"
    )


class Media(Base):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, index=True)
    link: Mapped[str]
    tweet_id: Mapped[int] = mapped_column(ForeignKey("tweets.id"), nullable=True)
