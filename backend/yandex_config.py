import os
import json
import requests
from typing import Dict, Optional


class YandexAuthManager:
    def __init__(self, config_file: str = "yandex_config.json"):
        self.config_file = config_file
        self.config = self._load_config()

    def _load_config(self) -> Dict:
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    def _save_config(self):
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, ensure_ascii=False, indent=2)

    def setup_auth(self):
        """Первоначальная настройка ключей"""
        print("🔑 Настройка Yandex Cloud API")
        print("=" * 50)

        self.config['YANDEX_API_KEY'] = input("1. IAM Token (из IAM Keys): ").strip()
        self.config['YANDEX_VISION_KEY'] = input("2. Vision API Key (из Marketplace): ").strip()
        self.config['YANDEX_STORAGE_BUCKET'] = input("3. Bucket name (из Object Storage): ").strip()
        self.config['YANDEX_STORAGE_ACCESS_KEY'] = input("4. Storage Access Key ID: ").strip()
        self.config['YANDEX_STORAGE_SECRET_KEY'] = input("5. Storage Secret Key: ").strip()
        self.config['SECRET_KEY'] = input("6. JWT Secret Key: ").strip()

        self._save_config()
        self._create_env_file()
        print("✅ Конфигурация сохранена!")

    def update_keys(self):
        """Обновление отдельных ключей"""
        print("🔄 Обновление ключей Yandex Cloud API")
        print("=" * 50)

        keys_to_update = {
            '1': ('YANDEX_API_KEY', 'IAM Token'),
            '2': ('YANDEX_VISION_KEY', 'Vision API Key'),
            '3': ('YANDEX_STORAGE_BUCKET', 'Bucket name'),
            '4': ('YANDEX_STORAGE_ACCESS_KEY', 'Storage Access Key ID'),
            '5': ('YANDEX_STORAGE_SECRET_KEY', 'Storage Secret Key'),
            '6': ('SECRET_KEY', 'JWT Secret Key'),
            '7': ('Все ключи', 'Полное обновление')
        }

        for key, (config_key, description) in keys_to_update.items():
            if key != '7':
                print(f"{key}. {description}: {self.config.get(config_key, 'Не установлен')}")

        choice = input("\nВыберите ключ для обновления (1-7): ").strip()

        if choice == '7':
            self.setup_auth()
        elif choice in keys_to_update:
            config_key, description = keys_to_update[choice]
            new_value = input(f"Введите новое значение для {description}: ").strip()
            self.config[config_key] = new_value
            self._save_config()
            self._create_env_file()
            print(f"✅ {description} обновлен!")
        else:
            print("❌ Неверный выбор")

    def _create_env_file(self):
        """Создает/обновляет .env файл"""
        env_content = f"""YANDEX_API_KEY={self.config['YANDEX_API_KEY']}
YANDEX_VISION_KEY={self.config['YANDEX_VISION_KEY']}
YANDEX_STORAGE_BUCKET={self.config['YANDEX_STORAGE_BUCKET']}
YANDEX_STORAGE_ACCESS_KEY={self.config['YANDEX_STORAGE_ACCESS_KEY']}
YANDEX_STORAGE_SECRET_KEY={self.config['YANDEX_STORAGE_SECRET_KEY']}
SECRET_KEY={self.config['SECRET_KEY']}
DATABASE_URL=sqlite:///app.db
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
BACKDOOR_PASSWORD=recovery_secret
"""
        with open('.env', 'w', encoding='utf-8') as f:
            f.write(env_content)

    def check_config_exists(self):
        return bool(self.config)

    def get_vision_key(self):
        return self.config.get('YANDEX_VISION_KEY', '')

    def get_storage_keys(self):
        return (
            self.config.get('YANDEX_STORAGE_ACCESS_KEY', ''),
            self.config.get('YANDEX_STORAGE_SECRET_KEY', ''),
            self.config.get('YANDEX_STORAGE_BUCKET', '')
        )


yandex_config = YandexAuthManager()