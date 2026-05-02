#!/usr/bin/env python3
"""Verifica integración Postgres + MinIO tras el job de ingesta."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "data/processed/manifest/ingest_report.json"


def check_report() -> bool:
    if not REPORT.is_file():
        print(f"FAIL: no existe {REPORT}")
        return False
    data = json.loads(REPORT.read_text())
    print("OK report:", json.dumps(data, indent=2))
    return data.get("valid_unique", 0) > 0


def check_postgres() -> bool:
    try:
        import psycopg2
    except ImportError:
        print("SKIP postgres: psycopg2 no instalado")
        return True

    url = os.environ.get(
        "DATABASE_URL",
        "postgresql://salle:salle_secret@localhost:5432/salle_hospital",
    )
    conn = psycopg2.connect(url)
    ok = True
    with conn.cursor() as cur:
        cur.execute(
            "SELECT COUNT(*) FROM pipeline_runs WHERE status = 'ok'::pipeline_status"
        )
        runs = cur.fetchone()[0]
        print(f"OK pipeline_runs (ok): {runs}")

        cur.execute("SELECT COUNT(*) FROM pipeline_events")
        events = cur.fetchone()[0]
        print(f"OK pipeline_events: {events}")

        cur.execute("SELECT COUNT(*) FROM data_quality_issues")
        issues = cur.fetchone()[0]
        print(f"OK data_quality_issues: {issues}")

        if runs == 0:
            print("FAIL: ningún pipeline_run en ok")
            ok = False
    conn.close()
    return ok


def check_minio() -> bool:
    try:
        from minio import Minio
    except ImportError:
        print("SKIP minio: librería no instalada")
        return True

    endpoint = os.environ.get("MINIO_ENDPOINT", "localhost:9000")
    access = os.environ.get("MINIO_ROOT_USER", "minioadmin")
    secret = os.environ.get("MINIO_ROOT_PASSWORD", "minioadmin")
    bucket = os.environ.get("MINIO_BUCKET", "xray-images")

    client = Minio(endpoint, access_key=access, secret_key=secret, secure=False)
    if not client.bucket_exists(bucket):
        print(f"FAIL: bucket '{bucket}' no existe")
        return False

    objects = list(client.list_objects(bucket, prefix="raw/", recursive=True))
    print(f"OK MinIO objetos en {bucket}/raw/: {len(objects)}")
    if len(objects) == 0:
        print("FAIL: sin objetos en MinIO (¿UPLOAD_MINIO=true?)")
        return False
    return True


def main() -> int:
    results = [
        check_report(),
        check_postgres(),
        check_minio(),
    ]
    if all(results):
        print("\n=== Verificación OK ===")
        return 0
    print("\n=== Verificación con fallos ===")
    return 1


if __name__ == "__main__":
    sys.exit(main())
