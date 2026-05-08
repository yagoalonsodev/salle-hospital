"""Alertas operativas en PostgreSQL (compartido API, pipeline, Airflow)."""

from __future__ import annotations

import os
from typing import Any

import psycopg2


def _conn():
    url = os.environ.get("DATABASE_URL")
    if not url:
        return None
    return psycopg2.connect(url)


def create_alert(
    *,
    title: str,
    message: str,
    severity: str = "warning",
    run_id: str | None = None,
) -> int | None:
    if severity not in ("info", "warning", "critical"):
        severity = "warning"
    conn = _conn()
    if not conn:
        return None
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO alerts (run_id, severity, title, message)
                VALUES (%s, %s::alert_severity, %s, %s)
                RETURNING alert_id
                """,
                (run_id, severity, title[:128], message[:4000]),
            )
            row = cur.fetchone()
        conn.commit()
        return int(row[0]) if row else None
    except Exception as exc:  # noqa: BLE001
        print(f"[db_alerts] omitido: {exc}", file=__import__("sys").stderr)
        return None
    finally:
        conn.close()


def alert_quality_batch(
    run_id: str,
    *,
    corrupt: int,
    incomplete: int,
    duplicate: int,
    threshold: int = 10,
) -> None:
    total = corrupt + incomplete + duplicate
    if total < threshold:
        return
    create_alert(
        title="Umbral de calidad de imágenes superado",
        message=(
            f"Run {run_id}: corruptas={corrupt}, incompletas={incomplete}, "
            f"duplicadas={duplicate}. Revisar data_quality_issues."
        ),
        severity="warning" if total < threshold * 5 else "critical",
        run_id=run_id,
    )
