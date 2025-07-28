from pydantic import BaseModel
import uuid
from typing import Optional, List
from crud.src.rewiews.schemas import Review
from datetime import datetime, date

from crud.src.tags.schemas import TagModel


class Book(BaseModel):
    uid: uuid.UUID
    title: str
    author: str
    publisher: str
    published_date: date
    page_count: int
    language: str
    created_at: datetime
    updated_at: Optional[datetime] = None

class BookDetailModel(Book):
    reviews: List[Review]
    tags: List[TagModel]

class BookCreateModel(BaseModel):
    title: str
    author: str
    publisher: str
    published_date: str
    page_count: int
    language: str

class BookUpdateModel(BaseModel):
    title: str
    author: str
    publisher: str
    page_count: int
    language: str