import uuid

from fastapi import APIRouter, Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from .schemas import ReviewCreateModel
from .services import ReviewService
from crud.src.auth.dependecies import get_current_user
from crud.src.db.main import get_session
from crud.src.db.models import User


review_service = ReviewService()

review_router = APIRouter()


@review_router.post("/{book_uid}")
async def add_review_to_book(
        book_uid: uuid.UUID,
        review_data: ReviewCreateModel,
        current_user: User = Depends(get_current_user),
        session: AsyncSession = Depends(get_session),
):
    new_review = await review_service.add_review_to_book(
        user_email=current_user.email,
        review_data=review_data,
        book_uid=book_uid,
        session=session,
    )
    return new_review