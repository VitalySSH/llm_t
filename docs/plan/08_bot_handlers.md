# Этап 8. Bot Service: aiogram dispatcher и handlers

## Файлы

### `bot_service/app/bot/dispatcher.py`

```python
"""Сборка aiogram-диспетчера."""
from aiogram import Bot, Dispatcher

from app.bot import handlers
from app.core.config import settings


def build_bot_and_dispatcher() -> tuple[Bot, Dispatcher]:
    """Создаёт Bot и Dispatcher с роутерами."""
    bot = Bot(token=settings.telegram_bot_token)
    dp = Dispatcher()
    dp.include_router(handlers.router)
    return bot, dp
```

### `bot_service/app/bot/handlers.py`

```python
"""Хэндлеры Telegram."""
from aiogram import F, Router
from aiogram.filters import Command, CommandObject
from aiogram.types import Message

from app.core.jwt import decode_and_validate
from app.infra.redis import get_redis
from app.tasks.llm_tasks import llm_request

router = Router()


def _key(tg_user_id: int) -> str:
    return f"token:{tg_user_id}"


@router.message(Command("start"))
async def cmd_start(message: Message) -> None:
    """Приветствие."""
    await message.answer(
        "Привет! Сначала пришли JWT командой "
        "/token <jwt>, затем задавай вопросы."
    )


@router.message(Command("token"))
async def cmd_token(
    message: Message, command: CommandObject
) -> None:
    """Сохраняет JWT в Redis."""
    token = (command.args or "").strip()
    if not token:
        await message.answer(
            "использование: /token <jwt>"
        )
        return
    try:
        decode_and_validate(token)
    except ValueError as e:
        await message.answer(f"токен не принят: {e}")
        return
    redis = get_redis()
    await redis.set(_key(message.from_user.id), token)
    await message.answer("токен сохранён")


@router.message(F.text)
async def on_text(message: Message) -> None:
    """Принимает запрос пользователя."""
    redis = get_redis()
    token = await redis.get(_key(message.from_user.id))
    if not token:
        await message.answer(
            "нет токена. получите JWT в Auth Service "
            "(http://localhost:8000/docs) и пришлите "
            "его командой /token <jwt>"
        )
        return
    try:
        decode_and_validate(token)
    except ValueError as e:
        await message.answer(
            f"токен невалиден: {e}. "
            "пришлите новый: /token <jwt>"
        )
        return
    llm_request.delay(message.chat.id, message.text)
    await message.answer("запрос принят, ожидайте ответа")
```

### `bot_service/app/bot/runner.py`

```python
"""Запуск polling aiogram."""
import asyncio

from app.bot.dispatcher import build_bot_and_dispatcher


async def main() -> None:
    bot, dp = build_bot_and_dispatcher()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
```

## Проверка импортов

```bash
cd bot_service
uv run python -c "from app.bot import handlers; print('ok')"
```

Должно напечатать `ok`.

## Коммит

```bash
git add bot_service
git commit -m "bot: aiogram dispatcher и handlers"
```

## Чек-лист

- [ ] 3 файла созданы
- [ ] Импорты не падают
- [ ] Коммит сделан
- [ ] **STOP**
