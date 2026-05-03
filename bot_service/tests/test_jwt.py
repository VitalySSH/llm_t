"""Тесты валидации JWT."""
from datetime import datetime, timedelta, timezone

import pytest
from jose import jwt

from app.core.config import settings
from app.core.jwt import decode_and_validate


def _make_token(sub: str = "1", expires_in: int = 60) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": sub,
        "role": "user",
        "iat": int(now.timestamp()),
        "exp": int(
            (
                now + timedelta(minutes=expires_in)
            ).timestamp()
        ),
    }
    return jwt.encode(
        payload,
        settings.jwt_secret,
        algorithm=settings.jwt_alg,
    )


def test_валидный_токен_декодируется():
    token = _make_token(sub="42")
    payload = decode_and_validate(token)
    assert payload["sub"] == "42"


def test_мусор_не_проходит():
    with pytest.raises(ValueError):
        decode_and_validate("просто_мусор")
