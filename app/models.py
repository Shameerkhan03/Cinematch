from .database import Base
from sqlalchemy import (
    Column,
    Integer,
    Boolean,
    String,
    DateTime,
    ForeignKey,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.sql.expression import text
from datetime import datetime


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, nullable=False)
    username = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=True)
    created_at = Column(
        TIMESTAMP(timezone=True), server_default=text("now()"), nullable=False
    )
    comments = relationship("Comment", back_populates="user")
    has_onboarded = Column(Boolean, default=False)


class BlacklistedToken(Base):
    __tablename__ = "blacklisted_tokens"

    id = Column(Integer, primary_key=True, index=True)
    token = Column(String, nullable=False, unique=True)
    blacklisted_at = Column(DateTime, default=datetime.utcnow)


class LikedMovie(Base):
    __tablename__ = "liked_movies"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    movie_id = Column(Integer, nullable=False)  # numeric movieId for CF
    movie_title = Column(String, nullable=False)  # for TMDB or frontend

    __table_args__ = (
        UniqueConstraint("user_id", "movie_id", name="unique_user_movie"),
    )

    user = relationship("User", backref="liked_movies")


class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    movie_id = Column(Integer, nullable=False)
    movie_title = Column(String, nullable=False)
    text_comment = Column(String, nullable=False)
    sentiment = Column(String, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=text("now()"))

    user = relationship("User", back_populates="comments")
