import asyncio
import logging
from pathlib import Path
from datetime import datetime
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from bot.bot import router, check_bot_online
from dotenv import load_dotenv
from os import getenv

# Настройка логирования
BASE_DIR = Path(__file__).resolve().parent
LOGS_DIR = BASE_DIR / "logs"
LOGS_DIR.mkdir(parents=True, exist_ok=True)

# Настройка логгера
logger = logging.getLogger("main")
logger.setLevel(logging.INFO)

# Форматтер для логов
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Файловый обработчик
log_file = LOGS_DIR / f"main_{datetime.now().strftime('%Y-%m-%d')}.log"
file_handler = logging.FileHandler(log_file)
file_handler.setFormatter(formatter)

# Консольный обработчик
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)

# Добавляем обработчики к логгеру
logger.addHandler(file_handler)
logger.addHandler(stream_handler)

async def main():
    # Загружаем переменные окружения
    load_dotenv()
    
    # Получаем токен бота из переменных окружения
    TOKEN = getenv('BOT_TOKEN')
    if not TOKEN:
        logger.error("BOT_TOKEN не найден в переменных окружения")
        raise ValueError("BOT_TOKEN не найден в переменных окружения")
    
    logger.info("Запуск бота...")
    
    # Инициализируем хранилище состояний и бота
    storage = MemoryStorage()
    bot = Bot(token=TOKEN)
    dp = Dispatcher(storage=storage)
    
    # Регистрируем роутер из bot.py
    dp.include_router(router)
    
    # Проверяем, доступен ли бот
    is_online = await check_bot_online(bot)
    if not is_online:
        logger.error("Не удалось проверить доступность бота. Завершение работы.")
        return
    
    try:
        # Запускаем бота и пропускаем накопившиеся сообщения
        logger.info("Бот запущен и ожидает сообщения")
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}", exc_info=True)
    finally:
        logger.info("Бот завершил работу")

if __name__ == "__main__":
    try:
        logger.info("Инициализация приложения")
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Бот остановлен пользователем")
    except Exception as e:
        logger.critical(f"Необработанная ошибка: {e}", exc_info=True)