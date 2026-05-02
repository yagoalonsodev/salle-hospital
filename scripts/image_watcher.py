#!/usr/bin/env python3
"""Watcher de nuevas radiografías en incoming/ → árbol raw + flag para Airflow."""

from __future__ import annotations

import logging
import os
import re
import shutil
import sys
import time
from pathlib import Path

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

sys.path.insert(0, str(Path(__file__).resolve().parent))
from watcher_state import log_event, set_pending  # noqa: E402

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s watcher — %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger("image_watcher")

DATA_ROOT = Path(os.environ.get("DATA_ROOT", "/opt/data"))
INCOMING_ROOT = Path(
    os.environ.get(
        "WATCH_INCOMING_DIR",
        str(DATA_ROOT / "raw/covid19_vs_pneumonia/incoming"),
    )
)
RAW_ROOT = Path(
    os.environ.get("RAW_ROOT", str(DATA_ROOT / "raw/covid19_vs_pneumonia"))
)
VALID_SPLITS = {"train", "test"}
VALID_FOLDERS = {"NORMAL", "PNEUMONIA", "COVID19"}
DEBOUNCE_SEC = float(os.environ.get("WATCHER_DEBOUNCE_SEC", "2.0"))

JPG_RE = re.compile(r"\.jpe?g$", re.I)


class IncomingHandler(FileSystemEventHandler):
    def __init__(self) -> None:
        self._pending_paths: dict[str, float] = {}

    def on_created(self, event) -> None:
        if event.is_directory:
            return
        path = Path(event.src_path)
        if not JPG_RE.search(path.name):
            return
        self._pending_paths[str(path)] = time.time()

    def on_moved(self, event) -> None:
        if event.is_directory:
            return
        path = Path(event.dest_path)
        if INCOMING_ROOT not in path.parents:
            return
        if not JPG_RE.search(path.name):
            return
        self._pending_paths[str(path)] = time.time()

    def flush_ready(self) -> None:
        now = time.time()
        ready = [
            p
            for p, t0 in list(self._pending_paths.items())
            if now - t0 >= DEBOUNCE_SEC
        ]
        for p in ready:
            self._pending_paths.pop(p, None)
            self._ingest_file(Path(p))

    def _ingest_file(self, src: Path) -> None:
        if not src.is_file():
            return
        try:
            rel = src.relative_to(INCOMING_ROOT)
        except ValueError:
            log.warning("Fuera de incoming: %s", src)
            return

        parts = rel.parts
        if len(parts) >= 3 and parts[0] in VALID_SPLITS and parts[1] in VALID_FOLDERS:
            split, folder = parts[0], parts[1]
            filename = parts[-1]
        elif len(parts) == 1:
            split, folder, filename = "train", "NORMAL", parts[0]
        else:
            log.warning("Ruta incoming no válida (use split/CLASE/archivo.jpg): %s", rel)
            return

        dest_dir = RAW_ROOT / split / folder
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest = dest_dir / filename
        if dest.resolve() == src.resolve():
            return
        if dest.exists():
            stem, suffix = dest.stem, dest.suffix
            dest = dest_dir / f"{stem}_{int(time.time())}{suffix}"

        shutil.move(str(src), str(dest))
        rel_dest = dest.relative_to(DATA_ROOT).as_posix()
        log.info("Movido %s → %s", src.name, rel_dest)
        log_event("image_moved", rel_dest, {"split": split, "folder": folder})
        set_pending("new_image")


def main() -> None:
    INCOMING_ROOT.mkdir(parents=True, exist_ok=True)
    for split in VALID_SPLITS:
        for folder in VALID_FOLDERS:
            (INCOMING_ROOT / split / folder).mkdir(parents=True, exist_ok=True)

    handler = IncomingHandler()
    observer = Observer()
    observer.schedule(handler, str(INCOMING_ROOT), recursive=True)
    observer.start()
    log.info("Vigilando %s (debounce %.1fs)", INCOMING_ROOT, DEBOUNCE_SEC)

    try:
        while True:
            handler.flush_ready()
            time.sleep(0.5)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


if __name__ == "__main__":
    main()
