import asyncio
import logging
from aiogram import Bot, Dispatcher

from app.config import BOT_TOKEN, LOG_LEVEL
from app.logging_cfg import setup_logging
from app.bot.handlers import router


def cli():
    asyncio.run(main())


async def main():
    if BOT_TOKEN is None:
        raise RuntimeError("BOT_TOKEN не задан в переменных окружения или .env")

    setup_logging(LOG_LEVEL)
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    dp.include_router(router)

    logging.getLogger(__name__).info("Bot started")
    await dp.start_polling(bot)


if __name__ == "__main__":
    cli()