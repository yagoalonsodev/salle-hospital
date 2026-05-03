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


def minio_config() -> tuple[str, str, str, str]:
    return (
        os.environ.get("MINIO_ENDPOINT", "minio:9000"),
        require_env("MINIO_ROOT_USER"),
        require_env("MINIO_ROOT_PASSWORD"),
        os.environ.get("MINIO_BUCKET", "xray-images"),
    )
