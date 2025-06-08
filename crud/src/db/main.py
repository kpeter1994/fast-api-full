from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import create_async_engine
from crud.src.config import Config



engine = create_async_engine(
    url=Config.DATABASE_URL,
    echo=True
)

async def init_db():
    async with engine.begin() as conn:
        from crud.src.books.models import Book

        await conn.run_sync(SQLModel.metadata.create_all)

