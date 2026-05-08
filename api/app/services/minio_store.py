"""Cliente MinIO para radiografías subidas."""

from __future__ import annotations

import io
from typing import Any

from minio import Minio
from minio.error import S3Error

from app.config import UPLOAD_PREFIX, minio_settings
from app.services.retry_util import retry_call


def _client() -> Minio:
    cfg = minio_settings()
    return Minio(
        cfg["endpoint"],
        access_key=cfg["access_key"],
        secret_key=cfg["secret_key"],
        secure=cfg["secure"],
    )


def check_minio() -> tuple[bool, str | None]:
    try:
        cfg = minio_settings()
        client = _client()
        if not client.bucket_exists(cfg["bucket"]):
            client.make_bucket(cfg["bucket"])
        return True, None
    except Exception as exc:  # noqa: BLE001
        return False, str(exc)


def upload_bytes(
    object_key: str,
    data: bytes,
    content_type: str = "image/jpeg",
) -> str:
    cfg = minio_settings()
    client = _client()
    bucket = cfg["bucket"]
    if not client.bucket_exists(bucket):
        client.make_bucket(bucket)
    def _put() -> None:
        client.put_object(
            bucket,
            object_key,
            io.BytesIO(data),
            length=len(data),
            content_type=content_type,
        )

    retry_call(_put, attempts=3, exceptions=(S3Error, OSError, ConnectionError))
    return object_key


def object_key_for_study(study_id: str, ext: str = ".jpg") -> str:
    return f"{UPLOAD_PREFIX}/{study_id}{ext}"


def delete_object(object_key: str) -> None:
    cfg = minio_settings()
    client = _client()
    client.remove_object(cfg["bucket"], object_key)


def download_bytes(object_key: str) -> bytes:
    cfg = minio_settings()
    client = _client()
    response = client.get_object(cfg["bucket"], object_key)
    try:
        return response.read()
    finally:
        response.close()
        response.release_conn()
