from passlib.context import CryptContext
from datetime import datetime, timedelta
from crud.src.config import Config
import jwt
import uuid
import logging
from itsdangerous import  URLSafeTimedSerializer

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ACCESS_TOKEN_EXPIRE_EXPIRY = 3600

def generate_phash(password: str) -> str:
    return password_context.hash(password)

def verify_password(password: str, hash: str) -> bool:
    return password_context.verify(password, hash)

def create_access_token(user_data: dict, expiry: timedelta = None, refresh: bool = False) -> str:
    payload = {}
    payload['user'] = user_data
    payload['exp'] = datetime.now() + (expiry if expiry is not None else timedelta(seconds=ACCESS_TOKEN_EXPIRE_EXPIRY))

    payload['jti'] = str(uuid.uuid4())

    payload['refresh'] = refresh

    token = jwt.encode(
        payload=payload,
        key=Config.JWT_SECRET,
        algorithm=Config.JWT_ALGORITHM,
    )

    return token

def decode_token(token: str) -> dict:
    try:
        token_data = jwt.decode(
            jwt=token,
            key=Config.JWT_SECRET,
            algorithms=[Config.JWT_ALGORITHM],
        )
        return token_data

    except jwt.PyJWTError as e:
        logging.exception(e)
        return None


serializer = URLSafeTimedSerializer(secret_key=Config.JWT_SECRET, salt="email-configuration")

def create_url_safe_token(data: dict) -> str:
    token = serializer.dumps(data)
    return token

def decode_url_safe_token(token: str):
    try:
        token_data = serializer.loads(token)
        return token_data
    except Exception as e:
        logging.error(str(e))