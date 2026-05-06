"""Catálogo de centros hospitalarios."""

from __future__ import annotations

from typing import Any

from psycopg2.extras import RealDictCursor

from app.db import get_conn


def list_active() -> list[dict[str, Any]]:
    with get_conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                SELECT site_code, site_name
                FROM sites
                WHERE active = TRUE
                ORDER BY site_name
                """
            )
            return [dict(r) for r in cur.fetchall()]


def exists(site_code: str) -> bool:
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT 1 FROM sites WHERE site_code = %s AND active = TRUE",
                (site_code,),
            )
            return cur.fetchone() is not None
