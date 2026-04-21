import uuid
from dataclasses import dataclass
from datetime import timedelta
from io import BytesIO

from fastapi import UploadFile
from minio import Minio
from minio.error import S3Error

from app.core.config import settings


@dataclass
class UploadResult:
    object_key: str
    storage_path: str


class MinIOClient:
    def __init__(self):
        self._client = Minio(
            endpoint=settings.minio_endpoint,
            access_key=settings.minio_access_key,
            secret_key=settings.minio_secret_key,
            secure=settings.minio_secure,
        )
        self._bucket = settings.minio_bucket
        self._bucket_ensured = False

    def _ensure_bucket(self) -> None:
        if not self._bucket_ensured:
            if not self._client.bucket_exists(self._bucket):
                self._client.make_bucket(self._bucket)
            self._bucket_ensured = True

    async def upload(self, file: UploadFile) -> UploadResult:
        self._ensure_bucket()
        content = await file.read()
        object_key = f"{uuid.uuid4().hex}/{file.filename}"
        self._client.put_object(
            bucket_name=self._bucket,
            object_name=object_key,
            data=BytesIO(content),
            length=len(content),
            content_type=file.content_type or "application/octet-stream",
        )
        await file.seek(0)
        return UploadResult(
            object_key=object_key,
            storage_path=f"{self._bucket}/{object_key}",
        )

    def _object_key_from_path(self, storage_path: str) -> str:
        return storage_path[len(self._bucket) + 1:]

    def delete(self, storage_path: str) -> None:
        object_key = self._object_key_from_path(storage_path)
        try:
            self._client.remove_object(self._bucket, object_key)
        except S3Error as e:
            raise RuntimeError(f"Failed to delete object {storage_path}") from e

    def get_presigned_url(self, storage_path: str) -> str:
        object_key = self._object_key_from_path(storage_path)
        try:
            return self._client.presigned_get_object(
                bucket_name=self._bucket,
                object_name=object_key,
                expires=timedelta(minutes=5),
            )
        except S3Error as e:
            raise RuntimeError(f"Failed to generate presigned URL for {storage_path}") from e


minio_client = MinIOClient()
