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
