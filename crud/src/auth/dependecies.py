from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Request, status
from .utils import decode_token
from fastapi.exceptions import HTTPException

class TokenBearer(HTTPBearer):

    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> HTTPAuthorizationCredentials | None:
        creds =  await super().__call__(request)

        token = creds.credentials

        token_data = decode_token(token)

        if not self.token_valid(token):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
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

class AccessTokenBearer(TokenBearer):
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
