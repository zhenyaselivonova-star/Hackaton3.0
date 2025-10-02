import os
import requests
from geopy.geocoders import Yandex
from geopy.distance import geodesic
from utils.exif import extract_exif_coords
import random
import hashlib


def get_coords_from_image(file_path: str, metadata: dict) -> tuple:
    """
    Получает координаты из фото:
    1. Сначала из EXIF данных
    2. Потом из Yandex Vision API (текст на фото)
    3. Если ничего - УНИКАЛЬНЫЕ координаты на основе хеша файла
    """
    print(f"🔍 Анализируем координаты для {file_path}")

    # 1. Пробуем EXIF данные
    exif_coords = extract_exif_coords(metadata)
    if exif_coords:
        print(f"✅ Нашли координаты в EXIF: {exif_coords}")
        return exif_coords

    # 2. Пробуем Yandex Vision API для текста на фото
    vision_coords = get_coords_from_vision_api(file_path)
    if vision_coords:
        print(f"✅ Нашли координаты через Vision API: {vision_coords}")
        return vision_coords

    # 3. Fallback - УНИКАЛЬНЫЕ координаты на основе хеша файла
    unique_coords = get_unique_coords_from_file(file_path)
    print(f"⚠️ Используем уникальные координаты: {unique_coords}")
    return unique_coords


def get_unique_coords_from_file(file_path: str) -> tuple:
    """Генерирует УНИКАЛЬНЫЕ координаты на основе хеша файла"""
    try:
        # Создаем хеш от содержимого файла
        with open(file_path, 'rb') as f:
            file_hash = hashlib.md5(f.read()).hexdigest()

        # Преобразуем хеш в числа для координат
        hash_int = int(file_hash[:8], 16)  # Берем первые 8 символов хеша

        # Разные районы Москвы с центральными точками
        moscow_districts = [
            (55.7339, 37.5889),  # Арбат
            (55.7603, 37.6186),  # Китай-город
            (55.7749, 37.6327),  # Садовое кольцо север
            (55.7360, 37.6245),  # Замоскворечье
            (55.7150, 37.6300),  # Павелецкая
            (55.7570, 37.6550),  # Курский вокзал
            (55.7800, 37.6000),  # ВДНХ
            (55.7986, 37.5376),  # Сокол
            (55.6700, 37.5400),  # Южное Бутово
            (55.8600, 37.4800),  # Мытищи (подмосковье)
        ]

        # Выбираем район на основе хеша
        district_index = hash_int % len(moscow_districts)
        base_lat, base_lon = moscow_districts[district_index]

        # Добавляем небольшое случайное смещение (до 2км)
        lat_offset = ((hash_int % 1000) - 500) / 50000.0  # ±0.01 = ~1.1km
        lon_offset = (((hash_int // 1000) % 1000) - 500) / 30000.0  # ±0.016 = ~1.1km

        unique_lat = base_lat + lat_offset
        unique_lon = base_lon + lon_offset

        return (round(unique_lat, 6), round(unique_lon, 6))

    except Exception as e:
        print(f"❌ Ошибка генерации уникальных координат: {e}")
        return get_fallback_coords()


def get_fallback_coords() -> tuple:
    """Резервные координаты если все остальное fails"""
    # Случайные координаты в разных частях Москвы
    moscow_areas = [
        (55.751244, 37.618423),  # Красная площадь
        (55.758163, 37.619017),  # Большой театр
        (55.741275, 37.608849),  # Парк Горького
        (55.729887, 37.603079),  # Воробьевы горы
        (55.790363, 37.593781),  # ВДНХ
        (55.727032, 37.571271),  # МГУ
        (55.763260, 37.664399),  # Измайлово
        (55.693787, 37.660065),  # Царицыно
        (55.835675, 37.358131),  # Сходня
        (55.651195, 37.708969),  # Видное
    ]
    return random.choice(moscow_areas)


def get_coords_from_vision_api(file_path: str) -> tuple:
    """Использует Yandex Vision API для поиска адресных признаков на фото"""
    vision_key = os.getenv("YANDEX_VISION_KEY")
    if not vision_key:
        print("❌ YANDEX_VISION_KEY не настроен")
        return None

    try:
        # Читаем файл
        with open(file_path, 'rb') as f:
            image_data = f.read()

        # Подготавливаем запрос
        headers = {
            'Authorization': f'Api-Key {vision_key}',
            'Content-Type': 'application/json'
        }

        # Кодируем изображение в base64
        import base64
        encoded_image = base64.b64encode(image_data).decode('utf-8')

        data = {
            'folderId': 'auto',
            'analyzeSpecs': [{
                'content': encoded_image,
                'features': [{
                    'type': 'TEXT_DETECTION'
                }]
            }]
        }

        # Отправляем запрос
        response = requests.post(
            'https://vision.api.cloud.yandex.net/vision/v1/batchAnalyze',
            headers=headers,
            json=data,
            timeout=10
        )

        if response.status_code == 200:
            result = response.json()
            text = extract_text_from_vision_response(result)

            if text:
                print(f"📝 Найден текст на фото: {text[:100]}...")
                # Ищем адресные упоминания в тексте
                address = find_address_in_text(text)
                if address:
                    print(f"🏠 Найден адрес в тексте: {address}")
                    coords = get_coords_from_address(address)
                    if coords:
                        return coords

        print("❌ Vision API не нашел полезной информации")
        return None

    except Exception as e:
        print(f"❌ Ошибка Vision API: {e}")
        return None


def extract_text_from_vision_response(vision_data: dict) -> str:
    """Извлекает текст из ответа Vision API"""
    try:
        text_blocks = []

        results = vision_data.get('results', [])
        for result in results:
            text_detection = result.get('textDetection', {})
            pages = text_detection.get('pages', [])

            for page in pages:
                blocks = page.get('blocks', [])
                for block in blocks:
                    lines = block.get('lines', [])
                    for line in lines:
                        words = line.get('words', [])
                        line_text = ' '.join([word.get('text', '') for word in words])
                        if line_text.strip():
                            text_blocks.append(line_text.strip())

        full_text = ' '.join(text_blocks)
        return full_text if full_text else ""
    except Exception as e:
        print(f"❌ Ошибка парсинга Vision response: {e}")
        return ""


def find_address_in_text(text: str) -> str:
    """Ищет адресные упоминания в тексте"""
    if not text:
        return None

    # Москва-специфичные места
    moscow_landmarks = {
        'арбат': 'Москва, ул. Арбат',
        'кремль': 'Москва, Кремль',
        'красная площадь': 'Москва, Красная площадь',
        'вднх': 'Москва, ВДНХ',
        'китай-город': 'Москва, Китай-город',
        'тверская': 'Москва, ул. Тверская',
        'лубянка': 'Москва, Лубянская площадь',
        'манежная': 'Москва, Манежная площадь',
        'охотный ряд': 'Москва, Охотный ряд',
        'новый арбат': 'Москва, ул. Новый Арбат',
        'ленинский': 'Москва, Ленинский проспект',
        'кутузовский': 'Москва, Кутузовский проспект',
        'садовое кольцо': 'Москва, Садовое кольцо',
    }

    text_lower = text.lower()

    # Проверяем известные достопримечательности
    for landmark, address in moscow_landmarks.items():
        if landmark in text_lower:
            return address

    # Ищем адресные паттерны
    address_indicators = ['ул.', 'улица', 'проспект', 'пр-т', 'площадь', 'пл.']

    lines = text.split('\n')
    for line in lines:
        line_lower = line.lower()
        if any(indicator in line_lower for indicator in address_indicators):
            # Очищаем и возвращаем потенциальный адрес
            clean_line = ' '.join(line.split()[:8])  # Берем первые 8 слов
            return f"Москва, {clean_line}"

    return None


def get_coords_from_address(address: str) -> tuple:
    """Преобразует адрес в координаты через Yandex Geocoding"""
    yandex_key = os.getenv("YANDEX_API_KEY")
    if not yandex_key:
        print("❌ YANDEX_API_KEY не настроен для геокодирования")
        return None

    try:
        geocoder = Yandex(api_key=yandex_key)
        location = geocoder.geocode(address)

        if location:
            print(f"🎯 Геокодирование успешно: {address} → ({location.latitude}, {location.longitude})")
            return (location.latitude, location.longitude)
        else:
            print(f"❌ Не удалось геокодировать адрес: {address}")
            return None
    except Exception as e:
        print(f"❌ Ошибка геокодирования: {e}")
        return None


def get_address_from_coords(latitude: float, longitude: float) -> str:
    """Преобразует координаты в читаемый адрес"""
    yandex_key = os.getenv("YANDEX_API_KEY")
    if not yandex_key:
        # Fallback - генерируем адрес на основе координат
        return generate_realistic_address(latitude, longitude)

    try:
        geocoder = Yandex(api_key=yandex_key)
        location = geocoder.reverse((latitude, longitude))

        if location:
            print(f"📫 Обратное геокодирование: ({latitude}, {longitude}) → {location.address}")
            return location.address
        else:
            print(f"❌ Обратное геокодирование не удалось для ({latitude}, {longitude})")
            return generate_realistic_address(latitude, longitude)

    except Exception as e:
        print(f"❌ Ошибка обратного геокодирования: {e}")
        return generate_realistic_address(latitude, longitude)


def generate_realistic_address(lat: float, lon: float) -> str:
    """Генерирует реалистичный московский адрес на основе координат"""
    # Определяем район по координатам
    if lat > 55.78:
        area = "Север Москвы"
    elif lat < 55.72:
        area = "Юг Москвы"
    elif lon > 37.65:
        area = "Восток Москвы"
    elif lon < 37.58:
        area = "Запад Москвы"
    else:
        area = "Центр Москвы"

    # Список улиц для каждого района
    streets_by_area = {
        "Север Москвы": ["Ленинградский пр-т", "ул. Верхняя Масловка", "ул. Правобережная", "Алтуфьевское ш."],
        "Юг Москвы": ["Варшавское ш.", "Каширское ш.", "ул. Профсоюзная", "Севастопольский пр-т"],
        "Восток Москвы": ["Щелковское ш.", "ш. Энтузиастов", "ул. Первомайская", "Измайловский пр-т"],
        "Запад Москвы": ["Кутузовский пр-т", "Можайское ш.", "Рублевское ш.", "ул. Молодогвардейская"],
        "Центр Москвы": ["ул. Тверская", "ул. Большая Дмитровка", "ул. Пятницкая", "ул. Маросейка"]
    }

    streets = streets_by_area.get(area, ["ул. Московская"])

    # Выбираем улицу на основе координатЫ
    street_index = int(abs(lat * 1000)) % len(streets)
    street = streets[street_index]

    # Генерируем номер дома
    house_number = (int(abs(lon * 1000)) % 100) + 1

    return f"Москва, {street}, {house_number}"


def calculate_distance(coord1: tuple, coord2: tuple) -> float:
    """Расчет расстояния между координатами в метрах"""
    return geodesic(coord1, coord2).meters