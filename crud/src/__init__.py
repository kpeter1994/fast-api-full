from fastapi import FastAPI
from crud.src.books.routes import book_router

version = "v1"
app = FastAPI(
    title="Bookly",
    description="Bookly API",
    version=version,
)

app.include_router(book_router, prefix=f"/api/{version}/books", tags=["books"])