from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import create_async_engine
from crud.src.config import Config
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import sessionmaker

engine = create_async_engine(
    url=Config.DATABASE_URL,
    echo=True
)

async def init_db():
    async with engine.begin() as conn:
        from crud.src.books.models import Book

        await conn.run_sync(SQLModel.metadata.create_all)

async def get_session() -> AsyncSession:
    Session = sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False
    )

    async with Session() as session:
        yield session