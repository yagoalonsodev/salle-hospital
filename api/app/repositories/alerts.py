"""Persistencia de alertas operativas."""

from __future__ import annotations

from typing import Any

from psycopg2.extras import RealDictCursor

from app.db import get_conn


def create_alert(
    *,
    title: str,
    message: str,
    severity: str = "warning",
    run_id: str | None = None,
) -> int | None:
    if severity not in ("info", "warning", "critical"):
        severity = "warning"
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO alerts (run_id, severity, title, message)
                VALUES (%s, %s::alert_severity, %s, %s)
                RETURNING alert_id
                """,
                (run_id, severity, title[:128], message),
            )
            row = cur.fetchone()
            return int(row[0]) if row else None


def list_alerts(*, limit: int = 50, unack_only: bool = False) -> list[dict[str, Any]]:
    with get_conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            q = """
                SELECT alert_id, run_id, severity, title, message,
                       acknowledged, created_at
                FROM alerts
            """
            if unack_only:
                q += " WHERE NOT acknowledged"
            q += " ORDER BY created_at DESC LIMIT %s"
            cur.execute(q, (limit,))
            rows = []
            for r in cur.fetchall():
                d = dict(r)
                if d.get("created_at"):
                    d["created_at"] = d["created_at"].isoformat()
                rows.append(d)
            return rows


def acknowledge_alert(alert_id: int) -> bool:
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE alerts SET acknowledged = TRUE WHERE alert_id = %s",
                (alert_id,),
            )
            return cur.rowcount > 0
