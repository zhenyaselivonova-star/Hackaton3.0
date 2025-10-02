from celery import Celery
import os

celery = Celery(__name__)
celery.conf.broker_url = os.getenv("CELERY_BROKER_URL")
celery.conf.result_backend = os.getenv("CELERY_RESULT_BACKEND")

@celery.task
def process_batch(tasks):
    # Batch processing logic
    return f"Processed {len(tasks)} tasks"