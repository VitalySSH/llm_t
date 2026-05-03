import asyncio

from app.bot.dispatcher import build_bot_and_dispatcher


async def main() -> None:
    bot, dp = build_bot_and_dispatcher()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
