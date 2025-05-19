import logging
from pathlib import Path
import uuid
import asyncio
from datetime import datetime

from aiogram import Router, F, Bot
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.enums import ContentType

from ml_model.model import SkinDiseaseModelYOLO
from dotenv import load_dotenv
from os import getenv

# Настройка логирования
BASE_DIR = Path(__file__).resolve().parent.parent
LOGS_DIR = BASE_DIR / "logs"
LOGS_DIR.mkdir(parents=True, exist_ok=True)

# Настройка логгера
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Форматтер для логов
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Файловый обработчик
log_file = LOGS_DIR / f"bot_{datetime.now().strftime('%Y-%m-%d')}.log"
file_handler = logging.FileHandler(log_file)
file_handler.setFormatter(formatter)

# Консольный обработчик
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)

# Добавляем обработчики к логгеру
logger.addHandler(file_handler)
logger.addHandler(stream_handler)

# Настройка временной директории
TEMP_DIR = BASE_DIR / "temp"
TEMP_DIR.mkdir(parents=True, exist_ok=True)

load_dotenv()
router = Router()

# Получение пути к весам модели
MODEL: str = getenv("MODEL", "ml_model/weights/yolo11n.pt")
logger.info(f"Инициализация модели из: {MODEL}")

# Инициализация модели
try:
    model = SkinDiseaseModelYOLO(MODEL)
    logger.info("Модель успешно инициализирована")
except Exception as e:
    logger.error(f"Ошибка инициализации модели: {e}")
    raise

# Состояния для управления диалогом
class PhotoStates(StatesGroup):
    waiting_for_photo = State()

# Обработчик команды /start
@router.message(CommandStart())
async def cmd_start(message: Message):
    user_id = message.from_user.id
    username = message.from_user.username or "Без имени пользователя"
    logger.info(f"Пользователь {username} (ID: {user_id}) запустил бота")
    
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📷 Анализ кожи")],
            [KeyboardButton(text="ℹ️ Информация")]
        ],
        resize_keyboard=True
    )
    
    await message.answer(
        "Добро пожаловать в Skin Disease Analyzer Bot!\n\n"
        "Я могу помочь определить возможные кожные заболевания по фото.\n\n"
        "Выберите действие на клавиатуре:",
        reply_markup=keyboard
    )

# Обработчик кнопки "Информация"
@router.message(F.text == "ℹ️ Информация")
async def info_handler(message: Message):
    user_id = message.from_user.id
    logger.info(f"Пользователь {user_id} запросил информацию")
    
    await message.answer(
        "**Skin Disease Analyzer Bot**\n\n"
        "Этот бот использует YOLOv8 для анализа фотографий кожи и определения возможных заболеваний.\n\n"
        "⚠️ *Важно: Бот не заменяет консультацию врача!* Результаты анализа являются предварительными и требуют подтверждения специалистом.\n\n"
        "Для анализа нажмите на кнопку '📷 Анализ кожи' и загрузите фотографию.",
        parse_mode="Markdown"
    )

# Обработчик кнопки "Анализ кожи"
@router.message(F.text == "📷 Анализ кожи")
async def analyze_button(message: Message, state: FSMContext):
    user_id = message.from_user.id
    logger.info(f"Пользователь {user_id} нажал кнопку 'Анализ кожи'")
    
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📸 Загрузить фото")],
            [KeyboardButton(text="↩️ Назад")]
        ],
        resize_keyboard=True
    )
    
    await message.answer(
        "Пожалуйста, загрузите фото кожи для анализа:",
        reply_markup=keyboard
    )
    await state.set_state(PhotoStates.waiting_for_photo)

# Обработчик кнопки "Назад"
@router.message(PhotoStates.waiting_for_photo, F.text == "↩️ Назад")
async def back_button(message: Message, state: FSMContext):
    user_id = message.from_user.id
    logger.info(f"Пользователь {user_id} вернулся в главное меню")
    
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📷 Анализ кожи")],
            [KeyboardButton(text="ℹ️ Информация")]
        ],
        resize_keyboard=True
    )
    
    await message.answer(
        "Выберите действие:",
        reply_markup=keyboard
    )
    await state.clear()

# Обработчик нажатия на кнопку "Загрузить фото"
@router.message(PhotoStates.waiting_for_photo, F.text == "📸 Загрузить фото")
async def upload_photo_button(message: Message):
    user_id = message.from_user.id
    logger.info(f"Пользователь {user_id} нажал кнопку 'Загрузить фото'")
    
    await message.answer("Отправьте фотографию кожи для анализа.")

# Обработчик фото - происходит анализ загруженного изображения
@router.message(PhotoStates.waiting_for_photo, F.content_type == ContentType.PHOTO)
async def handle_photo(message: Message, state: FSMContext):
    user_id = message.from_user.id
    logger.info(f"Пользователь {user_id} загрузил фото")
    
    try:
        # Получаем наибольшее фото (последнее в списке)
        photo = message.photo[-1]
        file_id = photo.file_id
        
        # Генерируем уникальное имя для файла
        filename = f"{uuid.uuid4().hex}.jpg"
        input_path = TEMP_DIR / filename
        
        logger.info(f"Сохранение фото от пользователя {user_id} в {input_path}")
        
        # Скачиваем файл
        await message.answer("Обрабатываю фото... Пожалуйста, подождите.")
        file = await message.bot.get_file(file_id)
        await message.bot.download_file(file.file_path, destination=input_path)
        
        logger.info(f"Фото сохранено, запуск модели для пользователя {user_id}")
        
        # Предсказание через YOLO
        result = model.predict(image_path=input_path)
        
        logger.info(f"Модель обработала фото пользователя {user_id}. Обнаружено: {len(result['detections'])} элементов")
        
        # Формируем ответ
        caption = "**Обнаружено:**\n"
        if result["detections"]:
            for item in result["detections"]:
                caption += f"- {item['name']} (вероятность: {item['confidence']*100:.1f}%)\n"
        else:
            caption += "Ничего не найдено.\n"
        
        caption += "\n⚠️ *Обратите внимание: результаты являются предварительными и требуют консультации врача.*"
        
        # Отправляем размеченное фото
        logger.info(f"Отправка результата пользователю {user_id}")
        
        keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="📷 Анализ кожи")],
                [KeyboardButton(text="ℹ️ Информация")]
            ],
            resize_keyboard=True
        )
        
        await message.answer_photo(
            photo=Path(result["output_image"]).open("rb"),
            caption=caption,
            parse_mode="Markdown",
            reply_markup=keyboard
        )
        
        # Сбрасываем состояние после обработки
        await state.clear()
        logger.info(f"Анализ для пользователя {user_id} завершен успешно")

    except Exception as e:
        logger.error(f"Ошибка при обработке фото пользователя {user_id}: {e}", exc_info=True)
        
        keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="📷 Анализ кожи")],
                [KeyboardButton(text="ℹ️ Информация")]
            ],
            resize_keyboard=True
        )
        
        await message.answer(
            "Произошла ошибка при обработке изображения. Пожалуйста, попробуйте другое фото или повторите попытку позже.",
            reply_markup=keyboard
        )
        await state.clear()

# Обработка других типов сообщений во время ожидания фото
@router.message(PhotoStates.waiting_for_photo)
async def wrong_input(message: Message):
    user_id = message.from_user.id
    logger.info(f"Пользователь {user_id} отправил неверный тип сообщения в режиме ожидания фото")
    
    await message.answer("Пожалуйста, отправьте фото или используйте кнопки на клавиатуре.")

# Функция для проверки работоспособности бота
async def check_bot_online(bot: Bot):
    """Функция для проверки работоспособности бота"""
    try:
        # Получаем информацию о боте
        bot_info = await bot.get_me()
        logger.info(f"Бот запущен! @{bot_info.username} ({bot_info.id})")
        return True
    except Exception as e:
        logger.error(f"Ошибка при проверке бота: {e}", exc_info=True)
        return False