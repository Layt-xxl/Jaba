from __future__ import annotations

import logging
from pathlib import Path
from ultralytics import YOLO
from typing import Tuple, List

logger = logging.getLogger(__name__)


class SkinDiseaseYOLO:
    """Singleton‑обёртка над YOLO."""

    _instance: "SkinDiseaseYOLO | None" = None

    def __new__(cls, weight_path: str | Path):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.model = YOLO(str(weight_path))
            logger.info("YOLO модель загружена из %s", weight_path)
        return cls._instance

    async def predict(self, image_path: str | Path) -> Tuple[Path, List[str], List[float]]:
        """Запускаем inference. Возвращаем путь к размеченному изображению + метки/конфиденсы."""
        image_path = Path(image_path)
        results = self.model.predict(source=str(image_path), save=True, imgsz=640)
        res = results[0]

        # Где Ultralytics сохранил картинку
        save_dir = Path(res.save_dir)  # type: ignore[attr-defined]
        annotated_path = save_dir / image_path.name

        # Имя класса и конфиденс из боксов
        names = self.model.names  # type: ignore[attr-defined]
        labels = [names[int(cls_idx)] for cls_idx in res.boxes.cls.tolist()]  # type: ignore
        confs = [float(c) for c in res.boxes.conf.tolist()]  # type: ignore

        return annotated_path, labels, confs