import uuid

from fastapi import APIRouter, HTTPException, status, Depends
from typing import List
from crud.src.books.schemas import BookUpdateModel, BookCreateModel, BookDetailModel
from crud.src.db.main import get_session
from sqlmodel.ext.asyncio.session import AsyncSession
from crud.src.books.services import BookService, Book
from crud.src.auth.dependecies import AccessTokenBearer, RoleChecker

book_router = APIRouter()
book_service = BookService()
access_token_bearer = AccessTokenBearer()
role_checker = Depends(RoleChecker(["admin", "user"]))

@book_router.get("/", response_model=List[Book], dependencies=[role_checker])
async def get_all_books(
        session:AsyncSession = Depends(get_session),
        token_details = Depends(access_token_bearer)
):
    books = book_service.get_all_books(session)
    return await books

@book_router.get("/user/{user_uid}", response_model=List[Book])
async def get_user_book_submissions(
        user_uid: uuid.UUID,
        session:AsyncSession = Depends(get_session),
        token_details: dict = Depends(access_token_bearer)
):
    books = book_service.get_user_books(user_uid, session)
    return await books

@book_router.post("/", status_code=status.HTTP_201_CREATED, response_model=Book, dependencies=[role_checker])
async def create_book(
        book_data:BookCreateModel,
        session:AsyncSession = Depends(get_session),
        token_details: dict = Depends(access_token_bearer),
) -> dict:
    user_uid = token_details.get("user")["user_uid"]
    new_book = book_service.create_book(book_data, user_uid ,session)
    return await new_book

@book_router.get("/{book_uid}", response_model=BookDetailModel)
async def get_book(
        book_uid: str,
        session:AsyncSession = Depends(get_session),
        token_details: dict = Depends(access_token_bearer)
) -> dict:
    book = await book_service.get_book(book_uid, session)
    if book is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    return book

@book_router.patch("/{book_uid}", response_model=Book, dependencies=[role_checker])
async def update_book(
        book_uid: str,
        book_data: BookUpdateModel,
        session:AsyncSession = Depends(get_session),
        token_details: dict = Depends(access_token_bearer),
) -> dict:
    updated_book = await book_service.update_book(book_uid, book_data, session)
    if updated_book is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    return  updated_book

@book_router.delete("/{book_uid}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[role_checker])
async def delete_book(
        book_uid: str,
        session:AsyncSession = Depends(get_session),
        token_details: dict = Depends(access_token_bearer),
):
    deleted_book = await book_service.delete_book(book_uid, session)
    if deleted_book is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    return

