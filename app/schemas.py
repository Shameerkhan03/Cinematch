from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str
    username: str
    user_id: int
    redirect: str


class TokenData(BaseModel):
    id: Optional[int] = None


class LikeCreate(BaseModel):
    movie_id: int
    movie_title: str


class MovieUnlike(BaseModel):
    movie_id: int


class LikedMovieOut(BaseModel):
    movie_id: int
    movie_title: str

    class Config:
        from_attributes = True


class CommentCreate(BaseModel):
    movie_id: int
    movie_title: str
    text_comment: str


class CommentOut(BaseModel):
    id: int
    movie_id: int
    movie_title: str
    text_comment: str
    user_id: int
    sentiment: str
    created_at: datetime

    class Config:
        from_attributes = True


class PasswordChangeWithCurrent(BaseModel):
    current_password: str
    new_password: str


class UsernameChange(BaseModel):
    new_username: str
