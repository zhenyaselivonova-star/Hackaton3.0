from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from app.schemas import UserCreate, Token
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta
import os
import logging
import hashlib

logger = logging.getLogger(__name__)

router = APIRouter()

SECRET_KEY = os.getenv("SECRET_KEY", "secret")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def get_password_hash(password: str) -> str:
    # Простой SHA256 хэш без ограничений длины
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return hashlib.sha256(plain_password.encode()).hexdigest() == hashed_password


@router.post("/register", response_model=Token)
def register(user: UserCreate, db: Session = Depends(get_db)):
    logger.info(f"🔐 Регистрация нового пользователя: {user.username}")
    logger.info(
        f"📝 Данные регистрации: username={user.username}, password_length={len(user.password) if user.password else 0}")

    try:
        logger.info("🔍 Поиск существующего пользователя...")
        db_user = db.query(User).filter(User.username == user.username).first()
        if db_user:
            logger.warning(f"❌ Пользователь {user.username} уже существует")
            raise HTTPException(status_code=400, detail="Username already registered")

        logger.info("🔐 Хэширование пароля...")
        hashed_password = get_password_hash(user.password)
        logger.info(f"✅ Пароль хэширован, длина хэша: {len(hashed_password)}")

        logger.info("💾 Создание нового пользователя в БД...")
        new_user = User(username=user.username, hashed_password=hashed_password)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        logger.info(f"✅ Пользователь {user.username} успешно создан в БД")

        logger.info("🎫 Генерация JWT токена...")
        access_token = jwt.encode(
            {"sub": user.username, "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)},
            SECRET_KEY,
            algorithm=ALGORITHM
        )
        logger.info(f"✅ Токен сгенерирован для пользователя {user.username}")

        return {"access_token": access_token, "token_type": "bearer"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"💥 КРИТИЧЕСКАЯ ОШИБКА при регистрации {user.username}: {str(e)}")
        logger.error(f"🔍 Тип ошибки: {type(e).__name__}")
        import traceback
        logger.error(f"📋 Stack trace: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/token", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    logger.info(f"🔐 Попытка входа пользователя: {form_data.username}")

    try:
        logger.info("🔍 Поиск пользователя в БД...")
        user = db.query(User).filter(User.username == form_data.username).first()

        if not user:
            logger.warning(f"❌ Пользователь {form_data.username} не найден")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password"
            )

        logger.info("🔐 Проверка пароля...")
        if not verify_password(form_data.password, user.hashed_password):
            logger.warning(f"❌ Неверный пароль для пользователя {form_data.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password"
            )

        logger.info("🎫 Генерация JWT токена...")
        access_token = jwt.encode(
            {"sub": user.username, "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)},
            SECRET_KEY,
            algorithm=ALGORITHM
        )
        logger.info(f"✅ Успешный вход для пользователя {form_data.username}")

        return {"access_token": access_token, "token_type": "bearer"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"💥 КРИТИЧЕСКАЯ ОШИБКА при входе {form_data.username}: {str(e)}")
        logger.error(f"🔍 Тип ошибки: {type(e).__name__}")
        import traceback
        logger.error(f"📋 Stack trace: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")