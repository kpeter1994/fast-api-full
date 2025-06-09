from fastapi import APIRouter, HTTPException, status, Depends
from typing import List
from crud.src.books.schemas import BookUpdateModel, BookCreateModel
from crud.src.db.main import get_session
from sqlmodel.ext.asyncio.session import AsyncSession
from crud.src.books.services import BookService, Book


book_router = APIRouter()
book_service = BookService()

@book_router.get("/", response_model=List[Book])
async def get_all_books(session:AsyncSession = Depends(get_session)):
    books = book_service.get_all_books(session)
    return await books


@book_router.post("/", status_code=status.HTTP_201_CREATED, response_model=Book)
async def create_book(book_data:BookCreateModel, session:AsyncSession = Depends(get_session)) -> dict:
    new_book = book_service.create_book(book_data, session)
    return await new_book

@book_router.get("/{book_uid}", response_model=Book)
async def get_book(book_uid: str, session:AsyncSession = Depends(get_session)) -> dict:
    book = await book_service.get_book(book_uid, session)
    if book is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    return book

@book_router.patch("/{book_uid}", response_model=Book)
async def update_book(book_uid: str, book_data: BookUpdateModel, session:AsyncSession = Depends(get_session)) -> dict:
    updated_book = await book_service.update_book(book_uid, book_data, session)
    if updated_book is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    return  updated_book

@book_router.delete("/{book_uid}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(book_uid: str, session:AsyncSession = Depends(get_session)):
    deleted_book = await book_service.delete_book(book_uid, session)
    if deleted_book is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    return

