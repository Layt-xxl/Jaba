import logging
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path


def setup_logging(level: str = "INFO", log_dir: str | Path = "logs") -> None:
    Path(log_dir).mkdir(exist_ok=True)
    log_file = Path(log_dir) / "skinbot.log"

    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        handlers=[
            logging.StreamHandler(),
            TimedRotatingFileHandler(log_file, when="midnight", backupCount=7, encoding="utf-8"),
        ],
    )