from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Request, status, Depends
from .utils import decode_token
from fastapi.exceptions import HTTPException
from crud.src.db.redis import token_blocklist, token_in_blocklist
from sqlmodel.ext.asyncio.session import AsyncSession
from crud.src.db.main import get_session
from .services import UserService
from crud.src.db.models import User
from typing import List

user_service = UserService()


class TokenBearer(HTTPBearer):

    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> HTTPAuthorizationCredentials | None:
        creds =  await super().__call__(request)

        token = creds.credentials

        token_data = decode_token(token)

        if not self.token_valid(token):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "error": "This token has been revoked or is invalid.",
                    "resolution": "Please login again to obtain a new token.",
                },
            )

        if await token_in_blocklist(token_data['jti']):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "error": "This token has been revoked or is invalid.",
                    "resolution": "Please login again to obtain a new token.",
                },
            )

        self.verify_token_data(token_data)

        return token_data

    def token_valid(self, token: str) -> bool:
        token_data = decode_token(token)

        if token_data is not None:
            return True

        return False

    def verify_token_data(self, token_data):
        raise NotImplementedError("Please Override this method in subclasses to verify token data.")

class  AccessTokenBearer(TokenBearer):
    def verify_token_data(self, token_data: dict) -> None:
        if token_data and token_data['refresh']:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Please provide a valid access token",
            )

class RefreshTokenBearer(TokenBearer):
    def verify_token_data(self, token_data: dict) -> None:
        if token_data and not token_data['refresh']:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Please provide a valid refresh token",
            )

async def get_current_user(token_details: dict = Depends(AccessTokenBearer()), session: AsyncSession = Depends(get_session)):
    user_email = token_details['user']['email']

    user = await user_service.get_user_by_email(user_email, session)

    return user

class RoleChecker:
    def __init__(self, allowed_roles: List[str]) -> None:
        self.allowed_roles = allowed_roles


    def __call__(self, current_user: User = Depends(get_current_user)):
        if current_user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to perform this action.",
            )
        return current_user