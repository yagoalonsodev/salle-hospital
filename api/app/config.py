"""Configuración desde variables de entorno."""

from __future__ import annotations

import os

MAX_UPLOAD_BYTES = int(os.environ.get("MAX_UPLOAD_BYTES", str(10 * 1024 * 1024)))
ALLOWED_EXTENSIONS = frozenset({".jpg", ".jpeg", ".png"})
MIN_IMAGE_SIDE = int(os.environ.get("MIN_IMAGE_SIDE", "64"))
MODEL_VERSION = os.environ.get("MODEL_VERSION", "rx_resnet50_v1")
UPLOAD_PREFIX = os.environ.get("MINIO_UPLOAD_PREFIX", "uploads")


def database_url() -> str:
    url = os.environ.get("DATABASE_URL")
    if not url:
        raise RuntimeError("Falta DATABASE_URL")
    return url


def ml_service_url() -> str:
    return os.environ.get("ML_SERVICE_URL", "http://ml:8001").rstrip("/")


def minio_settings() -> dict[str, str | bool]:
    return {
        "endpoint": os.environ.get("MINIO_ENDPOINT", "minio:9000"),
        "access_key": os.environ.get("MINIO_ROOT_USER", "minioadmin"),
        "secret_key": os.environ.get("MINIO_ROOT_PASSWORD", "minioadmin"),
        "bucket": os.environ.get("MINIO_BUCKET", "xray-images"),
        "secure": os.environ.get("MINIO_SECURE", "false").lower() == "true",
    }
