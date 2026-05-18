#!/usr/bin/env python3
"""Consulta rápida de logs en MongoDB (desde host o contenedor)."""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))
from mongo_log_store import get_collection, mongodb_uri  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Consultar logs en MongoDB")
    parser.add_argument(
        "--collection",
        default="application_logs",
        choices=("application_logs", "airflow_logs", "file_logs"),
    )
    parser.add_argument("--service", help="Filtrar por service (api, ml, watcher, …)")
    parser.add_argument("--limit", type=int, default=20)
    args = parser.parse_args()

    if not mongodb_uri():
        print("MONGODB_URI no configurada", file=sys.stderr)
        return 1

    coll = get_collection(args.collection)
    if coll is None:
        print("No se pudo conectar a MongoDB", file=sys.stderr)
        return 1

    query: dict = {}
    if args.service:
        query["service"] = args.service

    cursor = coll.find(query).sort("timestamp", -1).limit(args.limit)
    for doc in cursor:
        ts = doc.get("timestamp")
        if isinstance(ts, datetime):
            ts = ts.isoformat()
        row = {
            "timestamp": ts,
            "level": doc.get("level"),
            "service": doc.get("service"),
            "logger": doc.get("logger"),
            "message": doc.get("message"),
        }
        print(json.dumps(row, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
