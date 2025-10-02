# !!!ЗАПУСК ЛОКАЛЬНО ДЛЯ ТЕСТА И ПРОСМОТРА ДОКУМЕНТАЦИИ КОМАНДА python run.py!!!

# Собери обра]
docker build -t building-api .

# Тест локально
docker run -p 8000:8000 --env-file .env building-api

# Залогинься в Yandex Container Registry
yc container registry configure-docker

# Собери для Yandex Cloud
docker build -t cr.yandex/crpgd0e2m********/building-api:latest .

# Запуши образ
docker push cr.yandex/crpgd0e2m********/building-api:latest

API готово! Базовый URL: https://your-container-id.containers.yandexcloud.net

Основные методы:

Регистрация - POST /auth/register

Логин - POST /auth/token

Загрузка фото - POST /uploads/ (multipart/form-data)

Поиск - POST /search/ (по координатам или адресу)

История - GET /search/history

Токен передавать в заголовке: Authorization: Bearer {token}

Документация доступна по: /docs (Swagger UI)

Примеры запросов и TypeScript типы есть в документации!"