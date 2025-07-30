from fastapi import APIRouter, Depends, status, BackgroundTasks
from .schems import UserCreateModel, UserModel, UserLoginModel, UserBookModel, EmailModel
from .services import UserService
from .utils import verify_password, decode_url_safe_token, create_url_safe_token
from crud.src.db.main import get_session
from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi.exceptions import HTTPException
from .utils import create_access_token, decode_token
from datetime import timedelta, datetime
from fastapi.responses import JSONResponse
from .dependecies import RefreshTokenBearer, AccessTokenBearer, get_current_user, RoleChecker
from crud.src.db.redis import add_jti_to_blocklist
from crud.src.errors import UserAlreadyExists, UserNotFound
from crud.src.mail import create_message, mail
from crud.src.config import Config

auth_router = APIRouter()
user_service = UserService()
role_checker = RoleChecker(["admin", "user"])

REFRESH_TOKEN_EXPIRY = 2

@auth_router.post("/send_mail")
async def send_mail(emails:EmailModel):
    emails = emails.addresses
    html = "<h1>Welcome to our service!</h1><p>Thank you for signing up.</p>"
    message = create_message(
        recipients=emails,
        subject="Welcome to our service!",
        body=html
    )

    await mail.send_message(message)

    return {"message": "Emails sent successfully"}

@auth_router.post("/signup", status_code=status.HTTP_201_CREATED)
async def create_user_account(
        user_date: UserCreateModel,
        bg_tasks: BackgroundTasks,
        session: AsyncSession = Depends(get_session),
):
    email = user_date.email
    if await user_service.user_exists(email, session):
        raise UserAlreadyExists
    new_user = await user_service.create_user(user_date, session)

    token = create_url_safe_token({"email": email})

    link = f"http://{Config.DOMAIN}/api/v1/users/verify/{token}"

    html_message = f"""
    <h1>Verify your email</h1>
    <p>Please click this <a href="{link}">link</a> to verify your email.</p>
    """

    message = create_message(
        recipients=[email],
        subject="Verify your email",
        body=html_message
    )

    await mail.send_message(message)

    return {
        "message": "User created successfully, please check your email to verify your account.",
        "user": new_user
    }

@auth_router.get("/verify/{token}")
async def verify_user_account(token: str, session: AsyncSession = Depends(get_session)):
    token_data = decode_url_safe_token(token)

    user_email = token_data.get("email")
    if user_email:
        user = await user_service.get_user_by_email(user_email, session)
        if not user:
            raise UserNotFound()

        await user_service.update_user(user, {"is_verified": True}, session)
        return JSONResponse(content={
            "message": "User verified successfully",
        }, status_code=status.HTTP_200_OK)
    return JSONResponse(content={
        "message": "Invalid token or user not found",
    }, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


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

