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
