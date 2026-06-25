from datetime import datetime, timedelta, timezone

from jose import jwt
from passlib.context import CryptContext

from app.core.config import settings

import secrets
import string

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

_failed_attempts: dict[str, list[datetime]] = {}

MAX_ATTEMPTS = 5
WIDNOW_MINUTES = 10

def generate_temp_password(length: int = 10) -> str:
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict) -> str:
    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )
    return encoded_jwt

def check_brute_force(identifier: str):
    now = datetime.now()
    attempts = _failed_attempts.get(identifier, [])
    attempts = [t for t in attempts if now - t < timedelta(minutes=WIDNOW_MINUTES)]
    
    if len(attempts) >= MAX_ATTEMPTS:
        raise ValueError("로그인 시도가 너무 많습니다. 잠시 후 다시 시도해주세요.")
    
    _failed_attempts[identifier] = attempts

def record_failed_attempt(identifier: str):
    _failed_attempts.setdefault(identifier, []).append(datetime.now())

def clear_attempts(identifier: str):
    _failed_attempts.pop(identifier, None)
