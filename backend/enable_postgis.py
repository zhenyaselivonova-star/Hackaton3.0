import os
from sqlalchemy import create_engine, text
from urllib.parse import quote_plus
from dotenv import load_dotenv

load_dotenv()

# Параметры подключения
host = "rc1a-58mnqe0l2npppa1u.mdb.yandexcloud.net"
port = "6432"
database = "building_db"
user = "building_user"
password = "Starlira21.RUHOSTIDkudatikat"

# Экранируем пароль
encoded_password = quote_plus(password)

# URL подключения
db_url = f"postgresql+psycopg2://{user}:{encoded_password}@{host}:{port}/{database}?sslmode=require"

print("Устанавливаем расширение PostGIS...")

try:
    engine = create_engine(db_url)

    with engine.connect() as conn:
        # Включаем расширение PostGIS
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS postgis;"))
        conn.commit()
        print("✅ Расширение PostGIS установлено!")

        # Проверяем что расширение работает
        result = conn.execute(text("SELECT PostGIS_Version();"))
        version = result.fetchone()
        print(f"✅ Версия PostGIS: {version[0]}")

except Exception as e:
    print(f"❌ Ошибка: {e}")