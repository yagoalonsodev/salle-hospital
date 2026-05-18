"""Utilidades para cargar configuración desde variables de entorno (sin secretos en código)."""

from __future__ import annotations

import os


def require_env(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise RuntimeError(
            f"Falta la variable de entorno {name}. "
            "Copia .env.example a .env y rellena los valores."
        )
    return value


def database_url() -> str:
    return require_env("DATABASE_URL")


def mongodb_uri() -> str | None:
    uri = os.environ.get("MONGODB_URI")
    if uri:
        return uri
    user = os.environ.get("MONGO_USER") or os.environ.get("POSTGRES_USER")
    password = os.environ.get("MONGO_PASSWORD") or os.environ.get("POSTGRES_PASSWORD")
    if not user or not password:
        return None
    host = os.environ.get("MONGO_HOST", "mongodb")
    port = os.environ.get("MONGO_PORT", "27017")
    db = os.environ.get("MONGO_DB", "salle_logs")
    return f"mongodb://{user}:{password}@{host}:{port}/{db}?authSource=admin"


def minio_config() -> tuple[str, str, str, str]:
    return (
        os.environ.get("MINIO_ENDPOINT", "minio:9000"),
        require_env("MINIO_ROOT_USER"),
        require_env("MINIO_ROOT_PASSWORD"),
        os.environ.get("MINIO_BUCKET", "xray-images"),
    )
