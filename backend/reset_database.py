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

print("Удаляем старые таблицы...")

try:
    engine = create_engine(db_url)

    with engine.connect() as conn:
        # Удаляем старые таблицы (если есть)
        conn.execute(text("DROP TABLE IF EXISTS tasks CASCADE;"))
        conn.execute(text("DROP TABLE IF EXISTS search_history CASCADE;"))
        conn.execute(text("DROP TABLE IF EXISTS users CASCADE;"))
        conn.commit()
        print("✅ Старые таблицы удалены!")

        # Создаем новые таблицы
        from app.database import Base

        Base.metadata.create_all(bind=engine)
        print("✅ Новые таблицы созданы!")

except Exception as e:
    print(f"❌ Ошибка: {e}")