# Этап 4. Auth Service: API, deps, main

## Файлы

### `auth_service/app/api/deps.py`

```python
"""Зависимости FastAPI."""
from typing import AsyncGenerator

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import ExpiredSignatureError, JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (
    InvalidTokenError,
    TokenExpiredError,
)
from app.core.security import decode_token
from app.db.session import AsyncSessionLocal
from app.repositories.users import UsersRepository
from app.usecases.auth import AuthUseCase

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Сессия БД."""
    async with AsyncSessionLocal() as session:
        yield session


def get_users_repo(
    session: AsyncSession = Depends(get_db),
) -> UsersRepository:
    return UsersRepository(session)


def get_auth_uc(
    repo: UsersRepository = Depends(get_users_repo),
) -> AuthUseCase:
    return AuthUseCase(repo)


def get_current_user_id(
    token: str = Depends(oauth2_scheme),
) -> int:
    """Возвращает user_id из JWT."""
    try:
        payload = decode_token(token)
    except ExpiredSignatureError:
        raise TokenExpiredError()
    except JWTError:
        raise InvalidTokenError()
    sub = payload.get("sub")
    if sub is None:
        raise InvalidTokenError()
    return int(sub)
```

### `auth_service/app/api/routes_auth.py`

```python
"""Эндпоинты auth-сервиса."""
from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm

from app.api.deps import get_auth_uc, get_current_user_id
from app.schemas.auth import RegisterRequest, TokenResponse
from app.schemas.user import UserPublic
from app.usecases.auth import AuthUseCase

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register",
    response_model=UserPublic,
    status_code=status.HTTP_201_CREATED,
)
async def register(
    data: RegisterRequest,
    uc: AuthUseCase = Depends(get_auth_uc),
):
    """Регистрация пользователя."""
    return await uc.register(data.email, data.password)


@router.post("/login", response_model=TokenResponse)
async def login(
    form: OAuth2PasswordRequestForm = Depends(),
    uc: AuthUseCase = Depends(get_auth_uc),
):
    """Логин: вернёт JWT."""
    token = await uc.login(form.username, form.password)
    return TokenResponse(access_token=token)


@router.get("/me", response_model=UserPublic)
async def me(
    user_id: int = Depends(get_current_user_id),
    uc: AuthUseCase = Depends(get_auth_uc),
):
    """Профиль по JWT."""
    return await uc.me(user_id)
```

### `auth_service/app/api/router.py`

```python
"""Сборка роутеров."""
from fastapi import APIRouter

from app.api import routes_auth

api_router = APIRouter()
api_router.include_router(routes_auth.router)
```

### `auth_service/app/main.py`

```python
"""Точка входа auth-сервиса."""
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.router import api_router
from app.core.config import settings
from app.db.base import Base
from app.db.session import engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Создаёт таблицы при старте."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(title=settings.app_name, lifespan=lifespan)
app.include_router(api_router)


@app.get("/health")
async def health():
    return {"status": "ok"}
```

## Локальная проверка

```bash
cd auth_service
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Открыть `http://localhost:8000/docs` — должен открыться Swagger
с эндпоинтами `/auth/register`, `/auth/login`, `/auth/me`,
`/health`. Останавливаем (`Ctrl+C`) — функциональную проверку
сделаем тестами на следующем этапе.

## Коммит

```bash
git add auth_service
git commit -m "auth: api, deps, main"
```

## Чек-лист

- [ ] 4 файла созданы
- [ ] Сервис стартует, Swagger открывается
- [ ] Коммит сделан
- [ ] **STOP**
