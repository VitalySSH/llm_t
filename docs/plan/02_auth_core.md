# Этап 2. Auth Service: конфиг, БД, security

## Файлы

### `auth_service/app/core/config.py`

```python
"""Настройки auth-сервиса."""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "auth-service"
    env: str = "local"
    jwt_secret: str
    jwt_alg: str = "HS256"
    access_token_expire_minutes: int = 60
    sqlite_path: str = "./auth.db"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
```

### `auth_service/app/core/security.py`

```python
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
```

> `decode_token` пробрасывает исключения `jose`
> (`ExpiredSignatureError`, `JWTError`) — на уровне `deps` они
> ловятся и превращаются в свои HTTP-исключения.

### `auth_service/app/core/exceptions.py`

```python
"""HTTP-исключения auth-сервиса."""
from fastapi import HTTPException


class BaseHTTPException(HTTPException):
    """База для своих HTTP-исключений."""

    status_code = 500
    detail = "internal error"

    def __init__(self) -> None:
        super().__init__(
            status_code=self.status_code, detail=self.detail
        )


class UserAlreadyExistsError(BaseHTTPException):
    status_code = 409
    detail = "пользователь уже существует"


class InvalidCredentialsError(BaseHTTPException):
    status_code = 401
    detail = "неверный email или пароль"


class InvalidTokenError(BaseHTTPException):
    status_code = 401
    detail = "неверный токен"


class TokenExpiredError(BaseHTTPException):
    status_code = 401
    detail = "срок действия токена истёк"


class UserNotFoundError(BaseHTTPException):
    status_code = 404
    detail = "пользователь не найден"


class PermissionDeniedError(BaseHTTPException):
    status_code = 403
    detail = "доступ запрещён"
```

### `auth_service/app/db/base.py`

```python
"""База SQLAlchemy."""
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Базовый класс ORM-моделей."""
```

### `auth_service/app/db/session.py`

```python
"""Async-сессия SQLAlchemy."""
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import settings

DATABASE_URL = f"sqlite+aiosqlite:///{settings.sqlite_path}"

engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)
```

### `auth_service/app/db/models.py`

```python
"""ORM-модели auth-сервиса."""
from datetime import datetime

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class User(Base):
    """Пользователь системы."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(
        String(255), unique=True, index=True, nullable=False
    )
    password_hash: Mapped[str] = mapped_column(
        String(255), nullable=False
    )
    role: Mapped[str] = mapped_column(
        String(32), default="user", nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
```

## Проверка

```bash
cd auth_service
uv run python -c "import app.core.security; print('ok')"
uv run python -c "import app.db.models; print('ok')"
```

Оба должны напечатать `ok`.

## Коммит

```bash
git add auth_service
git commit -m "auth: конфиг, бд, security"
```

## Чек-лист

- [ ] 6 файлов созданы
- [ ] Импорты не падают
- [ ] Коммит сделан
- [ ] **STOP**
