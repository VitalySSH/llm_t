# Этап 7. Bot Service: OpenRouter и Celery-задача

## Файлы

### `bot_service/app/services/openrouter_client.py`

```python
"""Клиент OpenRouter."""
import httpx

from app.core.config import settings


async def call_openrouter(prompt: str) -> str:
    """Запрос в OpenRouter, возвращает текст ответа."""
    url = (
        f"{settings.openrouter_base_url}/chat/completions"
    )
    headers = {
        "Authorization": (
            f"Bearer {settings.openrouter_api_key}"
        ),
        "HTTP-Referer": settings.openrouter_site_url,
        "X-Title": settings.openrouter_app_name,
        "Content-Type": "application/json",
    }
    payload = {
        "model": settings.openrouter_model,
        "messages": [
            {"role": "user", "content": prompt}
        ],
    }
    async with httpx.AsyncClient(timeout=60) as cli:
        r = await cli.post(
            url, json=payload, headers=headers
        )
    if r.status_code != 200:
        raise RuntimeError(
            f"openrouter ошибка {r.status_code}: {r.text}"
        )
    data = r.json()
    return data["choices"][0]["message"]["content"]
```

### `bot_service/app/tasks/llm_tasks.py`

```python
"""Celery-задачи."""
import asyncio

from aiogram import Bot

from app.core.config import settings
from app.infra.celery_app import celery_app
from app.services.openrouter_client import call_openrouter


async def _process(tg_chat_id: int, prompt: str) -> None:
    """Запрос в LLM и отправка ответа в Telegram."""
    try:
        answer = await call_openrouter(prompt)
    except Exception as e:
        answer = f"ошибка LLM: {e}"
    bot = Bot(token=settings.telegram_bot_token)
    try:
        await bot.send_message(tg_chat_id, answer)
    finally:
        await bot.session.close()


@celery_app.task(name="llm_request")
def llm_request(tg_chat_id: int, prompt: str) -> None:
    """Вход Celery-задачи."""
    asyncio.run(_process(tg_chat_id, prompt))
```

## Проверка

```bash
cd bot_service
uv run python -c "import app.tasks.llm_tasks as t; print(t.llm_request.name)"
```

Должно напечатать `llm_request`.

## Коммит

```bash
git add bot_service
git commit -m "bot: openrouter и celery-задача"
```

## Чек-лист

- [ ] 2 файла созданы
- [ ] Импорт `llm_request` отрабатывает
- [ ] Коммит сделан
- [ ] **STOP**
