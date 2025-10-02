from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
import shutil
from pathlib import Path
from PIL import Image
import logging
from app.database import get_db
from app.models import Task
from app.schemas import TaskResponse
from services.detection import detect_buildings, detect_scene
from services.geo import get_coords_from_image, get_address_from_coords
from services.storage import upload_to_yandex_storage
from utils.exif import extract_metadata
from app.dependencies import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter()

TEMP_DIR = Path("uploads")
TEMP_DIR.mkdir(exist_ok=True)


@router.post("/", response_model=List[TaskResponse])
async def upload_files(
        files: List[UploadFile] = File(...),
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    logger.info("📥 UPLOAD ENDPOINT CALLED")
    logger.info(f"👤 User: {current_user.id}, Files: {len(files)}")

    tasks = []

    try:
        for file in files:
            logger.info(f"📄 Processing file: {file.filename}")

            # Сохраняем временный файл
            temp_path = TEMP_DIR / file.filename
            logger.info(f"💾 Saving to temp: {temp_path}")

            try:
                with temp_path.open("wb") as buffer:
                    shutil.copyfileobj(file.file, buffer)
                logger.info(f"✅ File saved: {temp_path}")
            except Exception as e:
                logger.error(f"❌ Error saving file: {e}")
                raise HTTPException(status_code=500, detail=f"Error saving file: {str(e)}")

            # Обрабатываем файл
            try:
                task = await process_file(str(temp_path), db, current_user.id)
                if task:
                    tasks.append(task)
                    logger.info(f"✅ File processed successfully: {file.filename}")
            except Exception as e:
                logger.error(f"❌ Error processing file {file.filename}: {e}")
                raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")
            finally:
                # Всегда удаляем временный файл
                try:
                    temp_path.unlink(missing_ok=True)
                    logger.info(f"🗑️ Temp file deleted: {temp_path}")
                except Exception as e:
                    logger.warning(f"⚠️ Could not delete temp file: {e}")

        logger.info(f"✅ UPLOAD COMPLETE: {len(tasks)} tasks created")
        return tasks

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"💥 UNEXPECTED ERROR in upload_files: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


async def process_file(file_path: str, db: Session, user_id: int):
    logger.info(f"🔧 Processing file: {file_path}")

    try:
        # Открываем и проверяем изображение
        logger.info(f"🖼️ Opening image: {file_path}")
        try:
            img = Image.open(file_path)
            logger.info(f"📐 Image size: {img.width}x{img.height}, format: {img.format}")

            if img.format not in ["JPEG", "PNG"]:
                logger.info(f"🔄 Converting image to PNG")
                converted_path = file_path + ".png"
                img.save(converted_path, "PNG")
                file_path = converted_path
                logger.info(f"✅ Image converted: {file_path}")

        except Exception as e:
            logger.error(f"❌ Invalid image format: {e}")
            raise HTTPException(status_code=400, detail=f"Invalid image format: {str(e)}")

        # Извлекаем метаданные
        logger.info("📊 Extracting metadata")
        try:
            metadata = extract_metadata(file_path)
            logger.info(f"✅ Metadata extracted: {metadata}")
        except Exception as e:
            logger.error(f"❌ Error extracting metadata: {e}")
            metadata = {}

        # Детекция зданий
        logger.info("🏢 Detecting buildings")
        try:
            bbox = detect_buildings(file_path)
            logger.info(f"✅ Buildings detected: {bbox}")
        except Exception as e:
            logger.error(f"❌ Error detecting buildings: {e}")
            bbox = {}

        # Детекция сцены
        logger.info("🌆 Detecting scene")
        try:
            scene = detect_scene(file_path)
            metadata["scene"] = scene
            logger.info(f"✅ Scene detected: {scene}")
        except Exception as e:
            logger.error(f"❌ Error detecting scene: {e}")
            metadata["scene"] = "unknown"

        # Получаем координаты
        logger.info("📍 Getting coordinates")
        try:
            lat, lon = get_coords_from_image(file_path, metadata)
            logger.info(f"✅ Coordinates: {lat}, {lon}")
        except Exception as e:
            logger.error(f"❌ Error getting coordinates: {e}")
            lat, lon = None, None

        # Получаем адрес
        logger.info("🏠 Getting address")
        try:
            address = get_address_from_coords(lat, lon) if lat and lon else "Адрес не определен"
            logger.info(f"✅ Address: {address}")
        except Exception as e:
            logger.error(f"❌ Error getting address: {e}")
            address = "Адрес не определен"

        # Загружаем в хранилище
        logger.info("☁️ Uploading to storage")
        try:
            storage_key = await upload_to_yandex_storage(file_path)
            logger.info(f"✅ Uploaded to storage: {storage_key}")
        except Exception as e:
            logger.error(f"❌ Error uploading to storage: {e}")
            storage_key = f"local/{Path(file_path).name}"

        # Сохраняем в БД
        logger.info("💾 Saving to database")
        try:
            # Добавляем координаты в метаданные для фронтенда
            image_metadata_with_coords = {
                **metadata,
                "latitude": lat,
                "longitude": lon
            }

            db_task = Task(
                filename=Path(file_path).name,
                original_filename=Path(file_path).name,
                storage_key=storage_key,
                status="completed",
                bbox=bbox,
                latitude=lat,
                longitude=lon,
                address=address,
                image_metadata=image_metadata_with_coords,  # ← Используем обновленные метаданные
                source="uploaded",
                resolution=f"{img.width}x{img.height}",
                user_id=user_id,
                processed_at=func.now()
            )
            db.add(db_task)
            db.commit()
            db.refresh(db_task)
            logger.info(f"✅ Task saved to DB: {db_task.id}")
        except Exception as e:
            logger.error(f"❌ Error saving to database: {e}")
            db.rollback()
            raise

        # Очистка
        try:
            if file_path.endswith(".png"):
                Path(file_path).unlink(missing_ok=True)
                logger.info(f"🗑️ Converted file deleted: {file_path}")
        except Exception as e:
            logger.warning(f"⚠️ Could not delete converted file: {e}")

        return db_task

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"💥 CRITICAL ERROR in process_file: {e}", exc_info=True)
        raise