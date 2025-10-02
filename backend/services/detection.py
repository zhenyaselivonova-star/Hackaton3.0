from PIL import Image
import cv2
import numpy as np


def detect_buildings(file_path: str) -> dict:
    """
    Детектирует здания на изображении.
    Пока использует простую логику, но можно подключить YOLO.
    """
    try:
        # Открываем изображение
        img = cv2.imread(file_path)
        if img is None:
            return {}

        height, width = img.shape[:2]

        # Простая логика детекции (можно улучшить)
        # Считаем что здание - это крупный объект в центре кадра
        center_x, center_y = width // 2, height // 2
        bbox_size = min(width, height) // 3

        bbox = {
            "x1": max(0, center_x - bbox_size),
            "y1": max(0, center_y - bbox_size),
            "x2": min(width, center_x + bbox_size),
            "y2": min(height, center_y + bbox_size),
            "width": width,
            "height": height,
            "confidence": 0.7
        }

        print(f"✅ Детектирован объект: {bbox}")
        return bbox

    except Exception as e:
        print(f"❌ Ошибка детекции: {e}")
        return {}


def detect_scene(file_path: str) -> list:
    """Определяет тип сцены на изображении"""
    try:
        with Image.open(file_path) as img:
            width, height = img.size
            aspect_ratio = width / height

            if aspect_ratio > 1.5:
                return ["urban", "landscape", "building"]
            elif aspect_ratio < 0.7:
                return ["architecture", "portrait", "building"]
            else:
                return ["building", "urban", "city"]

    except Exception as e:
        print(f"❌ Ошибка определения сцены: {e}")
        return ["building", "urban"]