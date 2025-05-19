from pathlib import Path
from typing import List, Dict, Union
from ultralytics import YOLO


class SkinDiseaseModelYOLO:
    def __init__(self, model_path: Union[str, Path] = "./weights/best.pt"):
        self.model_path = Path(model_path)
        self.model = YOLO(str(self.model_path))

    def predict(
        self,
        image_path: Union[str, Path],
        save_dir: Union[str, Path] = "predictions/",
        box_thickness: int = 2,
        font_size: float = 0.5,
        box_color: Union[tuple, None] = None
    ) -> Dict[str, Union[str, List[Dict[str, Union[str, float]]]]]:
        image_path = Path(image_path)
        save_dir = Path(save_dir)
        save_dir.mkdir(parents=True, exist_ok=True)


        results = self.model.predict(
            source=str(image_path),
            save=True,
            project=str(save_dir),
            name="",  # сохранение прямо в save_dir
            exist_ok=True,
            verbose=False,
        )

        detections = []
        for result in results:
            for box in result.boxes:
                class_id = int(box.cls[0])
                confidence = float(box.conf[0])
                name = self.model.names[class_id]
                detections.append({
                    "name": name,
                    "confidence": round(confidence, 4)
                })

        output_path = save_dir / image_path.name

        return {
            "output_image": str(output_path),
            "detections": detections
        }

    def fine_tune(
        self,
        data_yaml: Union[str, Path],
        epochs: int = 20,
        batch: int = 16,
        lr0: float = 0.001,
        img_size: int = 640,
        weights_save_path: Union[str, Path] = "ml_model/weights"
    ):
        """
        Дообучение модели. Веса сохраняются в указанной директории без создания exp-папок.

        :param data_yaml: путь к .yaml файлу с описанием данных
        :param epochs: количество эпох
        :param batch: размер батча
        :param lr0: начальная скорость обучения
        :param img_size: размер изображений
        :param weights_save_path: путь для сохранения весов (папка)
        """
        weights_save_path = Path(weights_save_path)
        weights_save_path.mkdir(parents=True, exist_ok=True)

        self.model.train(
            data=str(data_yaml),
            epochs=epochs,
            batch=batch,
            lr0=lr0,
            imgsz=img_size,
            project=str(weights_save_path),
            name="",  # сохранение прямо в указанной папке
            exist_ok=True,
            verbose=True
        )

        print(f"✅ Дообучение завершено. Веса сохранены в: {weights_save_path}")