import boto3
import os
from botocore.client import Config
from pathlib import Path


# Инициализация клиента S3
def get_s3_client():
    """Получение клиента S3 с проверкой credentials"""
    endpoint = "https://storage.yandexcloud.net"
    bucket_name = os.getenv("YANDEX_STORAGE_BUCKET")
    access_key = os.getenv("YANDEX_STORAGE_ACCESS_KEY")
    secret_key = os.getenv("YANDEX_STORAGE_SECRET_KEY")

    if not all([bucket_name, access_key, secret_key]):
        return None, None

    try:
        s3 = boto3.client(
            's3',
            endpoint_url=endpoint,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            config=Config(signature_version='s3v4')
        )
        return s3, bucket_name
    except Exception as e:
        print(f"S3 client error: {e}")
        return None, None


async def upload_to_yandex_storage(file_path: str) -> str:
    """Загрузка файла в Yandex Object Storage"""
    s3, bucket_name = get_s3_client()
    if not s3:
        return "storage_not_configured"

    key = Path(file_path).name
    try:
        s3.upload_file(file_path, bucket_name, key)
        return key
    except Exception as e:
        print(f"Upload error: {e}")
        return f"upload_error_{str(e)}"


async def get_presigned_url(key: str, expires_in=3600) -> str:
    """Генерация presigned URL для доступа к файлу"""
    s3, bucket_name = get_s3_client()
    if not s3 or key.startswith(("storage_not_configured", "upload_error")):
        return f"http://localhost:8000/static/{key}"

    try:
        return s3.generate_presigned_url(
            'get_object',
            Params={'Bucket': bucket_name, 'Key': key},
            ExpiresIn=expires_in
        )
    except Exception as e:
        print(f"Presigned URL error: {e}")
        return f"http://localhost:8000/static/{key}"