import os
from sqlalchemy import create_engine, text
from urllib.parse import quote_plus


def test_connection():
    try:
        # Твой хост
        host = "rc1a-58mnqe0l2npppa1u.mdb.yandexcloud.net"
        password = "Starlira21.RUHOSTIDkudatikat"

        print(f"Пытаемся подключиться к хосту: {host}")

        # Экранируем пароль
        encoded_password = quote_plus(password)

        # URL подключения
        db_url = f"postgresql+psycopg2://building_user:{encoded_password}@{host}:6432/building_db?sslmode=require"

        print(f"URL: postgresql+psycopg2://building_user:****@{host}:6432/building_db")

        engine = create_engine(db_url)

        # Тестируем подключение
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version();"))
            version = result.fetchone()
            print("✅ Подключение к PostgreSQL успешно!")
            print(f"Версия PostgreSQL: {version[0]}")

        return True

    except Exception as e:
        print(f"❌ Ошибка подключения: {e}")
        print(f"Тип ошибки: {type(e).__name__}")
        return False


if __name__ == "__main__":
    test_connection()