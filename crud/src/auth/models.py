from sqlmodel import SQLModel, Field, Column, Relationship
from typing import List, Optional
import uuid
from crud.src.books import models
from datetime import datetime
import sqlalchemy.dialects.postgresql as pg


class User(SQLModel, table=True):
    __tablename__ = "users"
    uid: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, sa_type=pg.UUID)
    username: str
    email: str
    name: str
    role: str = Field(sa_column=Column(pg.VARCHAR, nullable=False, server_default="user"))
    is_verified: bool = False
    password_hash: str = Field(exclude=True)
    created_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, default=datetime.now))
    update_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, default=datetime.now))
    books: List["models.Book"] = Relationship(back_populates="user", sa_relationship_kwargs={"lazy": "selectin"})

    def __repr__(self):
        return f"<User {self.username} ({self.email})>"
