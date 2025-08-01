import datetime
from typing import Optional
from pydantic import BaseModel, Field
from typing import List
from crud.src.books.schemas import Book
import uuid

from crud.src.rewiews.schemas import Review


class UserCreateModel(BaseModel):
    username: str = Field(max_length=8)
    name: str = Field(max_length=20)
    email: str = Field(max_length=40)
    password: str = Field(min_length=6)


class UserModel(BaseModel):
    uid: uuid.UUID
    username: str
    name: str = Field(max_length=20)
    email: str
    is_verified: bool
    password_hash: str = Field(exclude=True)
    created_at: datetime.datetime
    updated_at: Optional[datetime.datetime] = None

class UserBookModel(UserModel):
    books: List[Book]
    reviews: List[Review]

class UserLoginModel(BaseModel):
    email: str = Field(max_length=40)
    password: str = Field(min_length=6)

class EmailModel(BaseModel):
    addresses: List[str]

class PasswordResetRequestModel(BaseModel):
    email: str

class PasswordResetConfirmModel(BaseModel):
    new_password: str = Field(min_length=6)
    confirm_new_password: str = Field(min_length=6)