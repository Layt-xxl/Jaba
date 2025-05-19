from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent / ".env", override=True)

BOT_TOKEN: str | None = os.getenv("BOT_TOKEN")
MODEL_PATH: Path = Path(os.getenv("MODEL_PATH", "app/ml/weights/best.pt"))
LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")