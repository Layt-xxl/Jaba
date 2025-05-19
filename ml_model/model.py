from ultralytics import YOLO

model = YOLO("./weights/yolo11n.pt")

results = model("./tests/photo_2024-11-15_23-31-05.jpg")
