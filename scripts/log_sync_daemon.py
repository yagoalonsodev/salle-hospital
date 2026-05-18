#!/usr/bin/env python3
"""Sincroniza logs en disco (Airflow, verify_stack) hacia MongoDB."""

from __future__ import annotations

import os
import re
import time
from datetime import datetime, timezone
from pathlib import Path

from mongo_log_store import insert_log_document, service_name
from salle_logging import setup_logging

log = setup_logging("log_sync")

AIRFLOW_LOG_ROOT = Path(os.environ.get("AIRFLOW_LOG_DIR", "/opt/airflow/logs"))
EXTRA_LOG_ROOTS = [
    Path(p.strip())
    for p in os.environ.get("EXTRA_LOG_DIRS", "/opt/logs").split(",")
    if p.strip()
]
SYNC_INTERVAL = int(os.environ.get("LOG_SYNC_INTERVAL_SEC", "60"))
_LINE_RE = re.compile(
    r"^\[(?P<ts>[^\]]+)\]\s+(?P<level>\w+)\s+\[(?P<logger>[^\]]+)\]\s+—\s+(?P<msg>.*)$"
)
_AIRFLOW_TS_RE = re.compile(r"^\[(?P<ts>[\d\-:,.\s+]+)\]\s+\{(?P<logger>[^}]+)\}\s+-\s+(?P<msg>.*)$")


def _parse_airflow_path(path: Path) -> dict[str, str]:
    parts = path.parts
    meta: dict[str, str] = {"path": str(path)}
    try:
        if "dag_id=" in str(path):
            for part in parts:
                if part.startswith("dag_id="):
                    meta["dag_id"] = part.split("=", 1)[1]
                elif part.startswith("run_id="):
                    meta["run_id"] = part.split("=", 1)[1]
                elif part.startswith("task_id="):
                    meta["task_id"] = part.split("=", 1)[1]
    except (IndexError, ValueError):
        pass
    return meta


def _parse_line(line: str) -> dict | None:
    line = line.rstrip("\n")
    if not line.strip():
        return None
    m = _LINE_RE.match(line) or _AIRFLOW_TS_RE.match(line)
    if not m:
        return {"message": line, "level": "INFO", "logger": "raw"}
    groups = m.groupdict()
    ts_raw = groups.get("ts")
    ts = datetime.now(timezone.utc)
    if ts_raw:
        for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S"):
            try:
                ts = datetime.strptime(ts_raw.strip()[:19], fmt).replace(tzinfo=timezone.utc)
                break
            except ValueError:
                continue
    return {
        "timestamp": ts,
        "level": groups.get("level", "INFO"),
        "logger": groups.get("logger", "airflow"),
        "message": groups.get("msg", line),
    }


def _cursor_key(path: Path) -> str:
    return str(path.resolve())


def _load_offset(coll, key: str) -> int:
    if coll is None:
        return 0
    row = coll.find_one({"_id": key})
    return int(row["offset"]) if row else 0


def _save_offset(coll, key: str, offset: int) -> None:
    if coll is None:
        return
    coll.update_one(
        {"_id": key},
        {"$set": {"offset": offset, "updated_at": datetime.now(timezone.utc)}},
        upsert=True,
    )


def _sync_file(path: Path, collection: str, coll_cursors) -> int:
    if not path.is_file() or path.stat().st_size == 0:
        return 0
    key = _cursor_key(path)
    offset = _load_offset(coll_cursors, key)
    size = path.stat().st_size
    if offset > size:
        offset = 0
    n = 0
    meta = _parse_airflow_path(path) if "airflow" in collection else {"path": str(path)}
    with path.open("r", encoding="utf-8", errors="replace") as fh:
        fh.seek(offset)
        for line in fh:
            parsed = _parse_line(line)
            if not parsed:
                continue
            doc = {
                **parsed,
                "service": service_name(),
                "source": "file",
                **meta,
            }
            if "timestamp" not in doc:
                doc["timestamp"] = datetime.now(timezone.utc)
            if insert_log_document(collection, doc):
                n += 1
        new_offset = fh.tell()
    _save_offset(coll_cursors, key, new_offset)
    return n


def _iter_log_files(root: Path) -> list[Path]:
    if not root.is_dir():
        return []
    return sorted(root.rglob("*.log"))


def sync_once() -> int:
    from mongo_log_store import get_collection

    cursors = get_collection("log_sync_cursors")
    total = 0
    for f in _iter_log_files(AIRFLOW_LOG_ROOT):
        total += _sync_file(f, "airflow_logs", cursors)
    for root in EXTRA_LOG_ROOTS:
        for f in _iter_log_files(root):
            total += _sync_file(f, "file_logs", cursors)
    return total


def main() -> None:
    log.info("log_sync iniciado (intervalo=%ds)", SYNC_INTERVAL)
    while True:
        try:
            n = sync_once()
            if n:
                log.info("sincronizados %d líneas nuevas a MongoDB", n)
        except Exception as exc:
            log.exception("error en sync: %s", exc)
        time.sleep(SYNC_INTERVAL)


if __name__ == "__main__":
    main()
