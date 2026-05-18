"""Logging centralizado servicio ML."""

from __future__ import annotations

import logging
import os
import sys


def setup_logging() -> None:
    level = getattr(logging, os.environ.get("LOG_LEVEL", "INFO").upper(), logging.INFO)
    root = logging.getLogger()
    if root.handlers:
        return
    h = logging.StreamHandler(sys.stdout)
    h.setFormatter(
        logging.Formatter(
            "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
            datefmt="%Y-%m-%dT%H:%M:%S",
        )
    )
    root.addHandler(h)
    root.setLevel(level)
    try:
        from pathlib import Path

        scripts = Path("/opt/scripts")
        if scripts.is_dir() and str(scripts) not in sys.path:
            sys.path.insert(0, str(scripts))
        from mongo_log_store import attach_mongo_handler

        attach_mongo_handler(root)
    except ImportError:
        pass
