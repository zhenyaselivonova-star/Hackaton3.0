import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from urllib.parse import quote_plus

# Берем настройки из .env файла
DB_HOST = os.getenv("DB_HOST", "rc1a-58mnqe0l2npppa1u.mdb.yandexcloud.net")
DB_PORT = os.getenv("DB_PORT", "6432")
DB_NAME = os.getenv("DB_NAME", "building_db")
DB_USER = os.getenv("DB_USER", "building_user")
DB_PASS = os.getenv("DB_PASS", "Starlira21.RUHOSTIDkudatikat")

print(f"Подключаемся к БД: {DB_HOST}")  # Для отладки

# Экранируем пароль
encoded_password = quote_plus(DB_PASS)

# Формируем URL для PostgreSQL
SQLALCHEMY_DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{encoded_password}@{DB_HOST}:{DB_PORT}/{DB_NAME}?sslmode=require"

print(f"Database URL: postgresql+psycopg2://{DB_USER}:****@{DB_HOST}:{DB_PORT}/{DB_NAME}")

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()