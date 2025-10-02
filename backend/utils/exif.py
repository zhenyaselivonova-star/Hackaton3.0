import exifread
import logging
from typing import Optional, Tuple

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def extract_metadata(file_path: str) -> dict:
    """Извлечение EXIF метаданных из файла"""
    try:
        logger.info(f"📁 Reading metadata from: {file_path}")

        with open(file_path, "rb") as f:
            tags = exifread.process_file(f, details=False)

        # Логируем какие теги найдены
        gps_tags = [tag for tag in tags.keys() if 'GPS' in tag]
        logger.info(f"📊 Found {len(gps_tags)} GPS tags: {gps_tags}")

        # Сохраняем оригинальные объекты exifread
        metadata = {}
        for tag, value in tags.items():
            metadata[str(tag)] = value

        logger.info(f"✅ Successfully extracted {len(metadata)} metadata tags")
        return metadata

    except Exception as e:
        logger.error(f"❌ Error extracting metadata from {file_path}: {e}")
        return {"error": str(e)}


def parse_dms(dms_value) -> Optional[float]:
    """Парсинг координат в формате градусы/минуты/секунды в десятичные градусы"""
    try:
        # Проверяем, что это объект exifread с значениями
        if hasattr(dms_value, 'values') and len(dms_value.values) >= 3:
            degrees = float(dms_value.values[0])
            minutes = float(dms_value.values[1])
            seconds = float(dms_value.values[2])

            result = degrees + minutes / 60 + seconds / 3600
            logger.debug(f"📐 DMS parsed: {degrees}° {minutes}' {seconds}\" -> {result}°")
            return result

        else:
            logger.warning(f"⚠️ Unexpected DMS format: {dms_value} (type: {type(dms_value)})")
            return None

    except Exception as e:
        logger.error(f"❌ Error parsing DMS value {dms_value}: {e}")
        return None


def extract_exif_coords(metadata: dict) -> Optional[Tuple[float, float]]:
    """Извлечение координат из EXIF данных"""
    try:
        logger.info("🔍 Checking for GPS coordinates in metadata...")

        # Выводим все GPS теги для отладки
        gps_tags = {k: v for k, v in metadata.items() if 'GPS' in k}
        logger.info(f"📍 Found {len(gps_tags)} GPS tags")

        for tag_name, tag_value in gps_tags.items():
            logger.debug(f"  {tag_name}: {tag_value}")

        # Проверяем наличие необходимых тегов
        required_tags = ['GPS GPSLatitude', 'GPS GPSLongitude']
        missing_tags = [tag for tag in required_tags if tag not in metadata]

        if missing_tags:
            logger.warning(f"❌ Missing required GPS tags: {missing_tags}")
            return None

        logger.info("✅ Found all required GPS coordinates in EXIF")

        # Парсим координаты
        lat = parse_dms(metadata['GPS GPSLatitude'])
        lon = parse_dms(metadata['GPS GPSLongitude'])

        if lat is None or lon is None:
            logger.error("❌ Failed to parse GPS coordinates")
            return None

        # Учитываем полушарие
        lat_ref = metadata.get('GPS GPSLatitudeRef')
        lon_ref = metadata.get('GPS GPSLongitudeRef')

        logger.info(f"🧭 GPS references - Lat: {lat_ref}, Lon: {lon_ref}")

        if lat_ref:
            lat_ref_str = str(lat_ref).strip()
            if lat_ref_str in ['S', 's']:
                logger.info("🔄 Converting latitude to Southern hemisphere")
                lat = -lat

        if lon_ref:
            lon_ref_str = str(lon_ref).strip()
            if lon_ref_str in ['W', 'w']:
                logger.info("🔄 Converting longitude to Western hemisphere")
                lon = -lon

        logger.info(f"📍 Final coordinates: {lat:.6f}, {lon:.6f}")
        return (lat, lon)

    except Exception as e:
        logger.error(f"❌ EXIF coordinate parsing error: {e}")
        return None


def debug_gps_structure(file_path: str):
    """Функция для отладки структуры GPS данных"""
    logger.info(f"🔧 Debugging GPS structure for: {file_path}")

    try:
        with open(file_path, "rb") as f:
            tags = exifread.process_file(f, details=False)

        gps_tags = {str(k): v for k, v in tags.items() if 'GPS' in k}

        if not gps_tags:
            logger.warning("❌ No GPS tags found in file")
            return

        logger.info("📋 GPS tags structure:")
        for tag_name, tag_value in gps_tags.items():
            logger.info(f"  {tag_name}:")
            logger.info(f"    Value: {tag_value}")
            logger.info(f"    Type: {type(tag_value)}")

            if hasattr(tag_value, 'values'):
                logger.info(f"    Values: {tag_value.values}")
                logger.info(f"    Values type: {[type(v) for v in tag_value.values]}")

            if hasattr(tag_value, '__dict__'):
                logger.info(f"    Dict keys: {tag_value.__dict__.keys()}")

            logger.info("    ---")

    except Exception as e:
        logger.error(f"❌ Debug error: {e}")


def get_image_coordinates(file_path: str) -> Optional[Tuple[float, float]]:
    """Основная функция для получения координат из изображения"""
    logger.info(f"🖼️ Processing image: {file_path}")

    # Сначала получим все метаданные
    metadata = extract_metadata(file_path)

    if "error" in metadata:
        logger.error(f"❌ Failed to extract metadata: {metadata['error']}")
        return None

    # Попробуем извлечь координаты
    coords = extract_exif_coords(metadata)

    if coords:
        lat, lon = coords
        logger.info(f"🎯 Successfully extracted coordinates: {lat:.6f}, {lon:.6f}")
        return coords
    else:
        logger.warning("❌ No coordinates found in image")
        # Для отладки покажем структуру GPS данных
        debug_gps_structure(file_path)
        return None


# Пример использования
if __name__ == "__main__":
    # Укажите путь к вашему изображению
    image_path = "your_image.jpg"  # Замените на путь к вашему файлу

    coordinates = get_image_coordinates(image_path)

    if coordinates:
        lat, lon = coordinates
        print(f"\n🎉 Coordinates found!")
        print(f"📍 Latitude: {lat:.6f}")
        print(f"📍 Longitude: {lon:.6f}")

        # Форматирование для карт
        print(f"\n🌐 Map links:")
        print(f"Google Maps: https://maps.google.com/?q={lat},{lon}")
        print(f"OpenStreetMap: https://www.openstreetmap.org/?mlat={lat}&mlon={lon}")
    else:
        print("\n❌ No coordinates found in the image")
        print("Possible reasons:")
        print("  - Image has no GPS data")
        print("  - GPS data is corrupted")
        print("  - File is not an image with EXIF data")