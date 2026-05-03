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
