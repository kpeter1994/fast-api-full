from fastapi import FastAPI
from crud.src.books.routes import book_router
from crud.src.auth.routes import auth_router
from crud.src.rewiews.routes import review_router
from contextlib import asynccontextmanager
from crud.src.db.main import init_db

@asynccontextmanager
async def life_span(app: FastAPI):
    print("server is starting........................................")
    await init_db()
    yield
    print("server has been stopped")

version = "v1"
app = FastAPI(
    title="Bookly",
    description="Bookly API",
    version=version,
)

app.include_router(book_router, prefix=f"/api/{version}/books", tags=["books"])
app.include_router(auth_router, prefix=f"/api/{version}/users", tags=["users"])
app.include_router(review_router, prefix=f"/api/{version}/reviews", tags=["reviews"])