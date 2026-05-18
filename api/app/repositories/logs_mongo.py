"""Consulta de logs centralizados en MongoDB."""

from __future__ import annotations

from datetime import datetime
from typing import Any


def _serialize_doc(doc: dict[str, Any]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for key, val in doc.items():
        if key == "_id":
            out["id"] = str(val)
            continue
        if isinstance(val, datetime):
            out[key] = val.isoformat()
        else:
            out[key] = val
    return out


def fetch_logs(
    collection: str = "application_logs",
    *,
    service: str | None = None,
    level: str | None = None,
    limit: int = 100,
) -> list[dict[str, Any]]:
    try:
        import sys
        from pathlib import Path

        scripts = Path("/opt/scripts")
        if scripts.is_dir() and str(scripts) not in sys.path:
            sys.path.insert(0, str(scripts))
        from mongo_log_store import get_collection
    except ImportError:
        return []

    coll = get_collection(collection)
    if coll is None:
        return []

    query: dict[str, Any] = {}
    if service:
        query["service"] = service
    if level:
        query["level"] = level.upper()

    limit = max(1, min(int(limit), 500))
    cursor = coll.find(query).sort("timestamp", -1).limit(limit)
    return [_serialize_doc(dict(doc)) for doc in cursor]
