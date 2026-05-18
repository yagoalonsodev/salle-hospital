"""Persistencia de logs en MongoDB (handler logging + utilidades)."""

from __future__ import annotations

import logging
import os
import sys
import traceback
from datetime import datetime, timezone
from typing import Any

_client = None
_warned = False


def _enabled() -> bool:
    flag = os.environ.get("MONGO_LOG_ENABLED", "true").lower()
    if flag in ("0", "false", "no", "off"):
        return False
    return bool(os.environ.get("MONGODB_URI") or _build_uri_from_parts())


def _build_uri_from_parts() -> str | None:
    user = os.environ.get("MONGO_USER") or os.environ.get("POSTGRES_USER")
    password = os.environ.get("MONGO_PASSWORD") or os.environ.get("POSTGRES_PASSWORD")
    host = os.environ.get("MONGO_HOST", "mongodb")
    port = os.environ.get("MONGO_PORT", "27017")
    db = os.environ.get("MONGO_DB", "salle_logs")
    if not user or not password:
        return None
    return f"mongodb://{user}:{password}@{host}:{port}/{db}?authSource=admin"


def mongodb_uri() -> str | None:
    return os.environ.get("MONGODB_URI") or _build_uri_from_parts()


def service_name() -> str:
    return os.environ.get("SERVICE_NAME", "unknown")


def get_client():
    global _client
    if _client is not None:
        return _client
    uri = mongodb_uri()
    if not uri:
        return None
    from pymongo import MongoClient

    _client = MongoClient(uri, serverSelectionTimeoutMS=3000)
    _client.admin.command("ping")
    return _client


def get_collection(name: str):
    client = get_client()
    if client is None:
        return None
    db_name = os.environ.get("MONGO_DB", "salle_logs")
    return client[db_name][name]


def insert_log_document(collection_name: str, doc: dict[str, Any]) -> bool:
    try:
        coll = get_collection(collection_name)
        if coll is None:
            return False
        coll.insert_one(doc)
        return True
    except Exception as exc:  # noqa: BLE001 — logging no debe tumbar el servicio
        _warn_once(f"[mongo_log] no se pudo escribir en {collection_name}: {exc}")
        return False


def _warn_once(msg: str) -> None:
    global _warned
    if not _warned:
        print(msg, file=sys.stderr)
        _warned = True


class MongoLogHandler(logging.Handler):
    """Envía cada registro de logging a MongoDB (colección application_logs)."""

    def __init__(self, collection: str = "application_logs") -> None:
        super().__init__()
        self.collection_name = collection

    def emit(self, record: logging.LogRecord) -> None:
        if not _enabled():
            return
        try:
            doc = {
                "timestamp": datetime.fromtimestamp(record.created, tz=timezone.utc),
                "level": record.levelname,
                "logger": record.name,
                "message": record.getMessage(),
                "service": service_name(),
                "source": "application",
                "module": record.module,
                "funcName": record.funcName,
                "lineno": record.lineno,
            }
            if record.exc_info and record.exc_info[0] is not None:
                doc["exception"] = "".join(traceback.format_exception(*record.exc_info))
            insert_log_document(self.collection_name, doc)
        except Exception:
            self.handleError(record)


def attach_mongo_handler(logger: logging.Logger | None = None) -> bool:
    """Añade handler MongoDB al logger (idempotente)."""
    if not _enabled():
        return False
    target = logger or logging.getLogger()
    for h in target.handlers:
        if isinstance(h, MongoLogHandler):
            return True
    try:
        get_client()
    except Exception as exc:
        _warn_once(f"[mongo_log] MongoDB no disponible: {exc}")
        return False
    handler = MongoLogHandler()
    handler.setLevel(logging.DEBUG)
    target.addHandler(handler)
    return True


