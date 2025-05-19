from aiogram import Router, Bot, F
from aiogram.types import Message, FSInputFile
from aiogram.filters import CommandStart, Command
from pathlib import Path
import logging
import tempfile

from app.config import BOT_TOKEN, MODEL_PATH
from app.ml.model import SkinDiseaseYOLO

router = Router()
logger = logging.getLogger(__name__)
model = SkinDiseaseYOLO(MODEL_PATH)


@router.message(CommandStart())
async def start(msg: Message, bot: Bot):
    await msg.answer(
        "Привет! Пришли фото кожи — попробую определить заболевание.\n"
        "⚠️ Не заменяет консультацию дерматолога."
    )


@router.message(Command("help"))
async def help_cmd(msg: Message):
    await msg.answer("/start — приветствие, /help — эта подсказка. Просто пришли фото.")


@router.message(F.photo)
async def handle_photo(msg: Message, bot: Bot):
    if BOT_TOKEN is None:
        await msg.answer("BOT_TOKEN не настроен.")
        return

    
    # Скачиваем изображение во временную папку
    photo = msg.photo[-1]
    file_id = photo.file_id
    temp_dir = Path(tempfile.gettempdir())
    dest = temp_dir / f"{photo.file_unique_id}.jpg"
    file = await msg.bot.get_file(file_id)
    await msg.bot.download_file(file.file_path, destination=dest)

    # Inference YOLO → получаем размеченную картинку
    annotated_path, labels, confs = await model.predict(dest)
    logger.info("Predicted %s – %s", labels, confs)

    caption = "".join(f"{l}: {c:.1%}" for l, c in zip(labels, confs))

    # aiogram v3: отправляем через FSInputFile
    file_to_send = FSInputFile(annotated_path, filename=annotated_path.name)
    await msg.answer_photo(photo=file_to_send, caption=caption)