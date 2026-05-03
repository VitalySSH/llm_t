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
