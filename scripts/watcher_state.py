"""Estado compartido entre watcher y Airflow."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path

DATA_ROOT = Path(os.environ.get("DATA_ROOT", "/opt/data"))
WATCHER_DIR = Path(os.environ.get("WATCHER_STATE_DIR", str(DATA_ROOT / "processed/watcher")))
PENDING_FLAG = WATCHER_DIR / "pending.flag"
EVENTS_LOG = WATCHER_DIR / "events.jsonl"


def ensure_dirs() -> None:
    WATCHER_DIR.mkdir(parents=True, exist_ok=True)


def log_event(event: str, path: str, extra: dict | None = None) -> None:
    ensure_dirs()
    row = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "event": event,
        "path": path,
        **(extra or {}),
    }
    with EVENTS_LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


def set_pending(reason: str = "new_images") -> None:
    ensure_dirs()
    PENDING_FLAG.write_text(
        json.dumps(
            {
                "pending": True,
                "reason": reason,
                "ts": datetime.now(timezone.utc).isoformat(),
            }
        ),
        encoding="utf-8",
    )


def clear_pending() -> None:
    if PENDING_FLAG.is_file():
        PENDING_FLAG.unlink()


def is_pending() -> bool:
    return PENDING_FLAG.is_file()
