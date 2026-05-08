"""Logging centralizado para scripts, watcher y jobs (Día 8)."""

from __future__ import annotations

import logging
import os
import sys


def setup_logging(name: str | None = None) -> logging.Logger:
    level_name = os.environ.get("LOG_LEVEL", "INFO").upper()
    level = getattr(logging, level_name, logging.INFO)
    root = logging.getLogger()
    if not root.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(
            logging.Formatter(
                "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
                datefmt="%Y-%m-%dT%H:%M:%S",
            )
        )
        root.addHandler(handler)
        root.setLevel(level)
    logger = logging.getLogger(name or "salle")
    return logger
