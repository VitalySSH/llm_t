from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest
from jose import jwt

from app.bot import handlers
from app.core.config import settings


def _make_token() -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": "1",
        "role": "user",
        "iat": int(now.timestamp()),
        "exp": int(
            (now + timedelta(minutes=10)).timestamp()
        ),
    }
    return jwt.encode(
        payload,
        settings.jwt_secret,
        algorithm=settings.jwt_alg,
    )


def _msg(text: str, user_id: int = 100, chat_id: int = 100):
    m = MagicMock()
    m.text = text
    m.from_user.id = user_id
    m.chat.id = chat_id
    m.answer = AsyncMock()
    return m


@pytest.mark.asyncio
async def test_token_сохраняется_в_redis(fake_redis):
    token = _make_token()
    command = MagicMock()
    command.args = token
    message = _msg(f"/token {token}")
    await handlers.cmd_token(message, command)
    saved = await fake_redis.get("token:100")
    assert saved == token
    message.answer.assert_awaited()


@pytest.mark.asyncio
async def test_текст_без_токена_не_зовёт_celery(
    fake_redis, mocker
):
    delay = mocker.patch.object(
        handlers.llm_request, "delay"
    )
    message = _msg("привет")
    await handlers.on_text(message)
    delay.assert_not_called()
    message.answer.assert_awaited()


@pytest.mark.asyncio
async def test_текст_с_токеном_зовёт_celery(
    fake_redis, mocker
):
    token = _make_token()
    await fake_redis.set("token:100", token)
    delay = mocker.patch.object(
        handlers.llm_request, "delay"
    )
    message = _msg("задача")
    await handlers.on_text(message)
    delay.assert_called_once()
    args = delay.call_args[0]
    assert args[0] == 100
    assert args[1] == "задача"
    message.answer.assert_awaited()
