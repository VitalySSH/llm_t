# Этап 9. Bot Service: тесты

## Файлы

### `bot_service/tests/conftest.py`

```python
"""Фикстуры для тестов bot-сервиса."""
import fakeredis.aioredis
import pytest_asyncio


@pytest_asyncio.fixture
async def fake_redis(monkeypatch):
    """Подменяет get_redis в handlers на fakeredis."""
    r = fakeredis.aioredis.FakeRedis(
        decode_responses=True
    )
    from app.bot import handlers
    monkeypatch.setattr(
        handlers, "get_redis", lambda: r
    )
    yield r
    await r.aclose()
```

### `bot_service/tests/test_jwt.py`

```python
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
```

### `bot_service/tests/test_handlers.py`

```python
"""Тесты Telegram-хэндлеров."""
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
```

### `bot_service/tests/test_openrouter.py`

```python
"""Интеграционный тест клиента OpenRouter."""
import pytest
import respx
from httpx import Response

from app.core.config import settings
from app.services.openrouter_client import call_openrouter


@pytest.mark.asyncio
async def test_call_openrouter_возвращает_текст():
    url = (
        f"{settings.openrouter_base_url}/chat/completions"
    )
    with respx.mock(assert_all_called=True) as mock:
        route = mock.post(url).mock(
            return_value=Response(
                200,
                json={
                    "choices": [
                        {"message": {"content": "ответ"}}
                    ]
                },
            )
        )
        text = await call_openrouter("вопрос")
        assert text == "ответ"
        assert route.called
```

## Запуск

```bash
cd bot_service
uv run pytest -v
```

Все тесты должны быть зелёными. Проверь также, что тесты
auth-сервиса всё ещё проходят:

```bash
cd ../auth_service
uv run pytest -v
```

## Коммит

```bash
git add bot_service
git commit -m "bot: тесты jwt, handlers, openrouter"
```

## Чек-лист

- [ ] 4 файла созданы
- [ ] `pytest -v` зелёный в `bot_service`
- [ ] `pytest -v` зелёный в `auth_service`
- [ ] Коммит сделан
- [ ] **STOP**
