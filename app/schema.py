from datetime import datetime
from pydantic import BaseModel, EmailStr
from typing import Optional

from pydantic.types import conint
from app.database import Base

'''Schemas for users'''


class UserCreate(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    email: EmailStr
    created_at: datetime

    class Config:
        orm_mode = True


'''Schemas for posts'''


class PostBase(BaseModel):
    title: str
    content: str
    published: bool = True


class PostCreate(PostBase):
    pass


class PostResponse(PostBase):
    id: int
    created_at: datetime
    owner_id: str
    owner: UserOut

    class Config:
        orm_mode = True


class PostOut(BaseModel):
    Post: PostResponse
    votes: int

    class Config:
        orm_mode = True


'''Schemas for auth'''


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    id: Optional[str] = None


'''Schemas for voting'''


class Vote(BaseModel):
    post_id: int
    dir: conint(le=1)
