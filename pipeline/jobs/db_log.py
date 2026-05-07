"""Registro opcional de pipeline_runs y data_quality_issues en PostgreSQL."""

from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Any

import psycopg2
from psycopg2.extras import execute_batch


def _conn():
    url = os.environ.get("DATABASE_URL")
    if not url:
        return None
    return psycopg2.connect(url)


def _safe_db(fn, *args, **kwargs) -> None:
    conn = _conn()
    if not conn:
        return
    try:
        fn(conn, *args, **kwargs)
        conn.commit()
    except Exception as exc:  # noqa: BLE001 — pipeline no debe fallar si falta el esquema
        print(f"[db_log] omitido: {exc}")
    finally:
        conn.close()


def start_run(run_id: str, job_name: str) -> None:
    def _do(conn):
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO pipeline_runs (run_id, job_name, stage, status, started_at)
                VALUES (%s, %s, 'ingesta_imagenes', 'running', %s)
                ON CONFLICT (run_id) DO NOTHING
                """,
                (run_id, job_name, datetime.now(timezone.utc)),
            )

    _safe_db(_do)


def finish_run(
    run_id: str,
    *,
    status: str,
    records_in: int,
    records_out: int,
    records_failed: int,
    error_message: str | None = None,
) -> None:
    def _do(conn):
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE pipeline_runs
                SET status = %s::pipeline_status,
                    records_in = %s,
                    records_out = %s,
                    records_failed = %s,
                    error_message = %s,
                    finished_at = %s
                WHERE run_id = %s
                """,
                (
                    status,
                    records_in,
                    records_out,
                    records_failed,
                    error_message,
                    datetime.now(timezone.utc),
                    run_id,
                ),
            )
            if status == "failed":
                cur.execute(
                    """
                    INSERT INTO alerts (run_id, severity, title, message)
                    VALUES (%s, 'critical', %s, %s)
                    """,
                    (
                        run_id,
                        f"Pipeline fallido: {run_id}",
                        (error_message or "Error sin detalle")[:2000],
                    ),
                )

    _safe_db(_do)


def log_event(
    run_id: str,
    event_id: str,
    stage: str,
    status: str,
    records: int,
    message: str,
) -> None:
    def _do(conn):
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO pipeline_events (event_id, run_id, stage, status, records, message, logged_at)
                VALUES (%s, %s, %s, %s::pipeline_status, %s, %s, %s)
                ON CONFLICT (event_id) DO NOTHING
                """,
                (
                    event_id,
                    run_id,
                    stage,
                    status,
                    records,
                    message,
                    datetime.now(timezone.utc),
                ),
            )

    _safe_db(_do)


def log_quality_issues(run_id: str, rows: list[dict[str, Any]], batch_size: int = 500) -> None:
    if not rows:
        return

    def _do(conn):
        with conn.cursor() as cur:
            execute_batch(
                cur,
                """
                INSERT INTO data_quality_issues (run_id, study_id, issue_type, details)
                VALUES (%s, NULL, %s::quality_issue_type, %s)
                """,
                [
                    (run_id, r["issue_type"], r["details"][:2000])
                    for r in rows
                ],
                page_size=batch_size,
            )

    _safe_db(_do)
