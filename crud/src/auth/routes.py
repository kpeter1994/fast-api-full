from fastapi import APIRouter, Depends, status
from .schems import UserCreateModel, UserModel, UserLoginModel, UserBookModel
from .services import UserService
from .utils import verify_password
from crud.src.db.main import get_session
from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi.exceptions import HTTPException
from .utils import create_access_token, decode_token
from datetime import timedelta, datetime
from fastapi.responses import JSONResponse
from .dependecies import RefreshTokenBearer, AccessTokenBearer, get_current_user, RoleChecker
from crud.src.db.redis import add_jti_to_blocklist

auth_router = APIRouter()
user_service = UserService()
role_checker = RoleChecker(["admin", "user"])

REFRESH_TOKEN_EXPIRY = 2

@auth_router.post("/signup", response_model=UserModel, status_code=status.HTTP_201_CREATED)
async def create_user_account(
        user_date: UserCreateModel,
        session: AsyncSession = Depends(get_session),
):
    email = user_date.email
    if await user_service.user_exists(email, session):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User already exists")
    new_user = await user_service.create_user(user_date, session)

    return new_user

@auth_router.post("/login")
async def login_user(login_data: UserLoginModel, session: AsyncSession = Depends(get_session)):
    email = login_data.email
    password = login_data.password

    user = await user_service.get_user_by_email(email, session)

    if user is not None:
        password_valid = verify_password(password, user.password_hash)

        if password_valid:
            access_token = create_access_token(
                user_data={
                    "email": user.email,
                    'user_uid': str(user.uid),
                    "role": user.role,
                }
            )

            refresh_token = create_access_token(
                user_data={
                    "email": user.email,
                    'user_uid': str(user.uid),
                },
                refresh=True,
                expiry=timedelta(days=REFRESH_TOKEN_EXPIRY),
            )

            return JSONResponse(
                content={
                    "message": "Login successful",
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "user": {
                        "email": user.email,
                        "uid": str(user.uid),
                    }
                }
            )

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Incorrect email or password",
    )

@auth_router.get("/me", response_model=UserBookModel)
async def get_current_user(user = Depends(get_current_user), _:bool = Depends(role_checker)):
    return user

@auth_router.get("/refresh_token")
async def get_new_access_token(token_details: dict = Depends(RefreshTokenBearer())):
    expiry_timestamp = token_details['exp']

    if datetime.fromisoformat(expiry_timestamp) > datetime.now():
        new_access_token = create_access_token(
            user_data=token_details['user'],
        )

        return JSONResponse(
            content={
                "access_token": new_access_token
            }
        )
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired or invalid")

@auth_router.get("/logout")
async def revooke_token(token_details:dict = Depends(AccessTokenBearer())):
    jti = token_details['jti']
    await add_jti_to_blocklist(jti)

    return JSONResponse(
        content={
            "message": "Token revoked successfully"
        },
        status_code=status.HTTP_200_OK
    )

