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
