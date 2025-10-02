from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from datetime import timedelta
from app.database import get_db
from app.models import Task, SearchHistory
from app.schemas import SearchRequest, TaskResponse, SearchHistoryResponse
from services.geo import get_coords_from_address, calculate_distance
from services.storage import get_presigned_url
from app.dependencies import get_current_user

router = APIRouter()


@router.post("/", response_model=List[TaskResponse])
async def search_images(
        request: SearchRequest,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    # Валидация входных данных
    if not request.latitude and not request.longitude and not request.address:
        raise HTTPException(status_code=400, detail="Provide coordinates or address")

    # Если есть адрес, но нет координат - геокодируем
    if request.address and (not request.latitude or not request.longitude):
        coords = get_coords_from_address(request.address)
        if coords:
            request.latitude, request.longitude = coords
        else:
            raise HTTPException(status_code=400, detail="Could not geocode address")

    # Если есть координаты, но нет адреса - получаем адрес
    if request.latitude and request.longitude and not request.address:
        from services.geo import get_address_from_coords
        request.address = get_address_from_coords(request.latitude, request.longitude)

    query = db.query(Task).filter(
        Task.user_id == current_user.id,
        Task.status == "completed"
    )

    # Фильтр по времени
    if request.time_interval_years:
        query = query.filter(
            Task.created_at >= func.now() - timedelta(days=request.time_interval_years * 365)
        )

    # Фильтр по источнику
    if request.source_filter != "all":
        query = query.filter(Task.source == request.source_filter)

    # Фильтр по минимальному score
    if request.min_score:
        query = query.filter(Task.confidence_score >= request.min_score)

    tasks = query.all()
    results = []

    for task in tasks:
        # Проверяем наличие координат у задачи
        if task.latitude is not None and task.longitude is not None:
            task_lat, task_lon = task.latitude, task.longitude

            # Рассчитываем расстояние
            dist = calculate_distance(
                (request.latitude, request.longitude),
                (task_lat, task_lon)
            )

            # Применяем принцип поиска
            if request.search_principle == "radius" and dist <= request.radius_km * 1000:
                # Получаем URL для скачивания
                task.download_url = await get_presigned_url(task.storage_key)
                # Добавляем информацию о расстоянии
                task.distance_km = round(dist / 1000, 2)
                results.append(task)
            elif request.search_principle == "nearest":
                task.download_url = await get_presigned_url(task.storage_key)
                task.distance_km = round(dist / 1000, 2)
                results.append(task)

    if not results:
        raise HTTPException(status_code=404, detail="No results found")

    # Сортировка результатов
    if request.search_principle == "nearest":
        results = sorted(results, key=lambda t: t.distance_km)
    else:
        results = sorted(results, key=lambda t: t.processed_at or t.created_at, reverse=True)

    # Ограничение количества результатов
    results = results[:request.max_results] if hasattr(request, 'max_results') else results[:20]

    # Сохранение в историю поиска
    history = SearchHistory(
        query_type="coords" if request.latitude else "address",
        params={
            "latitude": request.latitude,
            "longitude": request.longitude,
            "address": request.address,
            "radius_km": request.radius_km,
            "principle": request.search_principle
        },
        results_count=len(results),
        user_id=current_user.id
    )
    db.add(history)
    db.commit()

    return results


@router.post("/by-coordinates", response_model=List[TaskResponse])
async def search_by_coordinates(
        latitude: float,
        longitude: float,
        radius_km: float = 1.0,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    """Прямой поиск по координатам"""
    if not latitude or not longitude:
        raise HTTPException(status_code=400, detail="Latitude and longitude are required")

    query = db.query(Task).filter(
        Task.user_id == current_user.id,
        Task.status == "completed",
        Task.latitude.isnot(None),
        Task.longitude.isnot(None)
    )

    tasks = query.all()
    results = []

    for task in tasks:
        dist = calculate_distance(
            (latitude, longitude),
            (task.latitude, task.longitude)
        )

        if dist <= radius_km * 1000:
            task.download_url = await get_presigned_url(task.storage_key)
            task.distance_km = round(dist / 1000, 2)
            results.append(task)

    results = sorted(results, key=lambda t: t.distance_km)[:10]
    return results


@router.get("/history", response_model=List[SearchHistoryResponse])
def get_history(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return db.query(SearchHistory).filter(SearchHistory.user_id == current_user.id).order_by(
        SearchHistory.created_at.desc()).all()