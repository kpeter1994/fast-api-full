from sqlmodel import SQLModel, Field, Column
import uuid
from datetime import datetime
import sqlalchemy.dialects.postgresql as pg


class User(SQLModel, table=True):
    __tablename__ = "users"
    uid: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, sa_type=pg.UUID)
    username: str
    email: str
    name: str
    is_verified: bool = False
    password_hash: str = Field(exclude=True)
    created_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, default=datetime.now))
    update_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, default=datetime.now))

    def __repr__(self):
        return f"<User {self.username} ({self.email})>"
