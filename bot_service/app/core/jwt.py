from jose import ExpiredSignatureError, JWTError, jwt

from app.core.config import settings


def decode_and_validate(token: str) -> dict:
    """Декодирует и валидирует токен.

    Бросает ValueError при ошибке.
    """
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=[settings.jwt_alg],
        )
    except ExpiredSignatureError as e:
        raise ValueError("токен истёк") from e
    except JWTError as e:
        raise ValueError("неверный токен") from e
    if "sub" not in payload:
        raise ValueError("в токене нет sub")
    return payload
