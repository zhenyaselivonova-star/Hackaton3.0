# test_import.py
import os
from dotenv import load_dotenv

load_dotenv()

print("Проверяем переменные окружения:")
print(f"DB_HOST: {os.getenv('DB_HOST')}")
print(f"DB_USER: {os.getenv('DB_USER')}")
print(f"DB_NAME: {os.getenv('DB_NAME')}")

from app.database import engine, Base

try:
    Base.metadata.create_all(bind=engine)
    print("✅ Таблицы созданы успешно!")
except Exception as e:
    print(f"❌ Ошибка: {e}")