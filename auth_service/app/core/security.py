"""Хеширование паролей и работа с JWT."""
from datetime import datetime, timedelta, timezone

from jose import jwt
from passlib.context import CryptContext

from app.core.config import settings

pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Хеш пароля."""
    return pwd_ctx.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    """Сверка пароля и хеша."""
    return pwd_ctx.verify(password, password_hash)


def create_access_token(sub: str, role: str = "user") -> str:
    """JWT с полями sub, role, iat, exp."""
    now = datetime.now(timezone.utc)
    exp = now + timedelta(
        minutes=settings.access_token_expire_minutes
    )
    payload = {
        "sub": sub,
        "role": role,
        "iat": int(now.timestamp()),
        "exp": int(exp.timestamp()),
    }
    return jwt.encode(
        payload, settings.jwt_secret, algorithm=settings.jwt_alg
    )


def decode_token(token: str) -> dict:
    """Декодирует JWT, валидирует подпись и срок."""
    return jwt.decode(
        token, settings.jwt_secret, algorithms=[settings.jwt_alg]
    )
