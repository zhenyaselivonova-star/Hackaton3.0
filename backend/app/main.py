import os
import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from app.database import engine, Base, get_db
from app import models
from routes import auth, uploads, search, maps, admin
from celery import Celery
from dotenv import load_dotenv

# Настройка логирования в реальном времени
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),  # Вывод в консоль
        logging.FileHandler('backend_debug.log', mode='w', encoding='utf-8')  # Лог файл
    ]
)
logger = logging.getLogger(__name__)

load_dotenv()

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Building Detection API",
    description="API для распознавания зданий, геокоординат и адресов",
    version="1.0.0"
)


# Middleware для детального логирования ВСЕХ запросов
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info("=" * 50)
    logger.info(f"📥 НОВЫЙ ЗАПРОС: {request.method} {request.url}")
    logger.info(f"📡 Клиент: {request.client.host}:{request.client.port}")
    logger.info(f"🎯 Путь: {request.url.path}")
    logger.info(f"🔍 Query params: {dict(request.query_params)}")
    logger.info(f"📋 Headers: {dict(request.headers)}")

    # Логируем тело запроса
    if request.method in ["POST", "PUT", "PATCH"]:
        try:
            body = await request.body()
            if body:
                body_str = body.decode('utf-8')
                logger.info(f"📦 Тело запроса ({len(body_str)} chars): {body_str}")
            else:
                logger.info("📦 Тело запроса: ПУСТО")
        except Exception as e:
            logger.error(f"❌ Ошибка чтения тела: {e}")

    try:
        response = await call_next(request)
        logger.info(f"📤 ОТВЕТ: {response.status_code}")

        # Логируем заголовки ответа
        logger.info(f"📋 Headers ответа: {dict(response.headers)}")

        return response
    except Exception as e:
        logger.error(f"💥 КРИТИЧЕСКАЯ ОШИБКА В ОБРАБОТЧИКЕ: {e}")
        raise


# Логируем запуск приложения
logger.info("🚀 Запуск FastAPI приложения...")

# Разрешаем все порты localhost
cors_origins = [
    "http://localhost:3000",
    "http://localhost:3001",
    "http://localhost:3002",
    "http://localhost:3003",
    "http://localhost:3004",
    "http://localhost:3005",
    "http://localhost:3006",
    "http://localhost:3007",
    "http://localhost:3008",
    "http://localhost:3009",
    "http://localhost:3010",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:3001",
    "http://127.0.0.1:3002",
    "http://127.0.0.1:3003",
    "http://127.0.0.1:3004",
    "http://127.0.0.1:3005",
    "http://127.0.0.1:3006",
    "http://127.0.0.1:3007",
    "http://127.0.0.1:3008",
    "http://127.0.0.1:3009",
    "http://127.0.0.1:3010",
    "http://localhost:5178",
    "http://localhost:5179",
    "http://localhost:5180",
    "http://localhost:5181",
]

logger.info(f"🌐 CORS разрешены для всех портов localhost (3000-3010, 5178-5181)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Логируем подключение роутеров
logger.info("🔗 Подключаем роутеры...")
app.include_router(auth.router, prefix="/auth", tags=["auth"])
logger.info("✅ Роутер auth подключен")
app.include_router(uploads.router, prefix="/uploads", tags=["uploads"])
logger.info("✅ Роутер uploads подключен")
app.include_router(search.router, prefix="/search", tags=["search"])
logger.info("✅ Роутер search подключен")
app.include_router(maps.router, prefix="/maps", tags=["maps"])
logger.info("✅ Роутер maps подключен")
app.include_router(admin.router, prefix="/admin", tags=["admin"])
logger.info("✅ Роутер admin подключен")

# Celery
celery = Celery(__name__,
                broker=os.getenv("CELERY_BROKER_URL"),
                backend=os.getenv("CELERY_RESULT_BACKEND"))


@app.get("/")
def root():
    logger.info("📍 Запрос к корневому эндпоинту /")
    return {"message": "API ready. Docs: /docs"}


@app.on_event("startup")
async def startup_event():
    logger.info("🎉 Приложение успешно запущено!")
    logger.info("📝 Документация доступна по адресу: http://localhost:8000/docs")


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("👋 Приложение останавливается...")


if __name__ == "__main__":
    import uvicorn

    logger.info("🔥 Запуск сервера uvicorn...")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="debug",  # Включаем дебаг логи uvicorn
        access_log=True  # Включаем логи доступа
    )
