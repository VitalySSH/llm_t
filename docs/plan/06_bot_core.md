# Этап 6. Bot Service: конфиг, JWT, infra, main

## Файлы

### `bot_service/app/core/config.py`

```python
"""Настройки bot-сервиса."""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "bot-service"
    env: str = "local"
    telegram_bot_token: str = ""
    jwt_secret: str
    jwt_alg: str = "HS256"
    redis_url: str = "redis://redis:6379/0"
    rabbitmq_url: str = (
        "amqp://guest:guest@rabbitmq:5672//"
    )
    openrouter_api_key: str = ""
    openrouter_base_url: str = (
        "https://openrouter.ai/api/v1"
    )
    openrouter_model: str = "stepfun/step-3.5-flash:free"
    openrouter_site_url: str = "https://example.com"
    openrouter_app_name: str = "bot-service"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
```

### `bot_service/app/core/jwt.py`

```python
"""Валидация JWT в bot-сервисе."""
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
```

### `bot_service/app/infra/redis.py`

```python
"""Redis-клиент."""
from redis.asyncio import Redis

from app.core.config import settings

_client: Redis | None = None


def get_redis() -> Redis:
    """Singleton-клиент Redis."""
    global _client
    if _client is None:
        _client = Redis.from_url(
            settings.redis_url, decode_responses=True
        )
    return _client
```

### `bot_service/app/infra/celery_app.py`

```python
"""Celery-приложение."""
from celery import Celery

from app.core.config import settings

celery_app = Celery(
    "bot_service",
    broker=settings.rabbitmq_url,
    backend=settings.redis_url,
)

# регистрация задач (импорт в конце во избежание цикла)
from app.tasks import llm_tasks  # noqa: E402, F401
```

> Импорт `llm_tasks` стоит в конце намеренно — чтобы `celery_app`
> уже был создан, когда задачи попытаются его импортировать.

### `bot_service/app/main.py`

```python
"""FastAPI bot-сервиса."""
from fastapi import FastAPI

from app.core.config import settings

app = FastAPI(title=settings.app_name)


@app.get("/health")
async def health():
    return {"status": "ok"}
```

## Важно

На этом этапе `app/tasks/llm_tasks.py` ещё не существует —
`celery_app.py` ломает импорт. Это **нормально** и ожидаемо,
импорт восстановится на следующем этапе. **Импорты celery_app
проверять не нужно.**

## Коммит

```bash
git add bot_service
git commit -m "bot: конфиг, jwt, infra, main"
```

## Чек-лист

- [ ] 5 файлов созданы
- [ ] Коммит сделан
- [ ] **STOP**
