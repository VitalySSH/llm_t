"""Тесты модуля security."""
from app.core.security import (
    create_access_token,
    decode_token,
    hash_password,
    verify_password,
)


def test_хеш_не_равен_паролю():
    h = hash_password("secret123")
    assert h != "secret123"


def test_верный_пароль_проходит():
    h = hash_password("secret123")
    assert verify_password("secret123", h) is True


def test_неверный_пароль_не_проходит():
    h = hash_password("secret123")
    assert verify_password("wrong", h) is False


def test_jwt_содержит_все_поля():
    token = create_access_token(sub="42", role="user")
    payload = decode_token(token)
    assert payload["sub"] == "42"
    assert payload["role"] == "user"
    assert "iat" in payload
    assert "exp" in payload
