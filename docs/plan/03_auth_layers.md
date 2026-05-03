# Этап 3. Auth Service: схемы, репозиторий, usecase

## Файлы

### `auth_service/app/schemas/auth.py`

```python
"""Схемы регистрации и токенов."""
from pydantic import BaseModel, EmailStr


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
```

### `auth_service/app/schemas/user.py`

```python
"""Публичные схемы пользователя."""
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr


class UserPublic(BaseModel):
    id: int
    email: EmailStr
    role: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
```

### `auth_service/app/repositories/users.py`

```python
"""Репозиторий пользователей."""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import User


class UsersRepository:
    """Доступ к таблице пользователей."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, user_id: int) -> User | None:
        """Найти по id."""
        return await self.session.get(User, user_id)

    async def get_by_email(self, email: str) -> User | None:
        """Найти по email."""
        stmt = select(User).where(User.email == email)
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def create(
        self,
        email: str,
        password_hash: str,
        role: str = "user",
    ) -> User:
        """Создать пользователя."""
        user = User(
            email=email,
            password_hash=password_hash,
            role=role,
        )
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user
```

### `auth_service/app/usecases/auth.py`

```python
"""Бизнес-логика auth-сервиса."""
from app.core.exceptions import (
    InvalidCredentialsError,
    UserAlreadyExistsError,
    UserNotFoundError,
)
from app.core.security import (
    create_access_token,
    hash_password,
    verify_password,
)
from app.db.models import User
from app.repositories.users import UsersRepository


class AuthUseCase:
    """Регистрация, логин, получение профиля."""

    def __init__(self, repo: UsersRepository) -> None:
        self.repo = repo

    async def register(
        self, email: str, password: str
    ) -> User:
        """Регистрирует нового пользователя."""
        if await self.repo.get_by_email(email):
            raise UserAlreadyExistsError()
        return await self.repo.create(
            email=email,
            password_hash=hash_password(password),
        )

    async def login(self, email: str, password: str) -> str:
        """Возвращает JWT при валидных данных."""
        user = await self.repo.get_by_email(email)
        if not user:
            raise InvalidCredentialsError()
        if not verify_password(password, user.password_hash):
            raise InvalidCredentialsError()
        return create_access_token(
            sub=str(user.id), role=user.role
        )

    async def me(self, user_id: int) -> User:
        """Профиль пользователя по id."""
        user = await self.repo.get_by_id(user_id)
        if not user:
            raise UserNotFoundError()
        return user
```

## Коммит

```bash
git add auth_service
git commit -m "auth: схемы, репозиторий, usecase"
```

## Чек-лист

- [ ] 4 файла созданы
- [ ] Импорты не падают
- [ ] Коммит сделан
- [ ] **STOP**
