from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional

class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str

class User(UserBase):
    pass
    id: int
    created_at: datetime

    class Config:
        ORM_MODE = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    id: Optional[int] = None

class PostBase(BaseModel):
    title: str
    content: str
    published: bool = True

class PostCreate(PostBase):
    pass

class Post(PostBase):
    pass
    id: int
    user_id: int
    created_at: datetime
    owner: User

    class Config:
        ORM_MODE = True

class Vote(BaseModel):
    post_id: int
    dir: int = Field(..., ge=0, le=1)

class PostOut(PostBase):
    Post: Post
    votes: int
