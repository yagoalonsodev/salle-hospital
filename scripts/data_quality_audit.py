#!/usr/bin/env python3
"""Auditoría de registros incompletos en BD → alertas (Día 8)."""

from __future__ import annotations

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from db_alerts import create_alert  # noqa: E402
from salle_logging import setup_logging  # noqa: E402

log = setup_logging("data_quality_audit")


def main() -> int:
    import psycopg2
    from psycopg2.extras import RealDictCursor

    url = os.environ.get("DATABASE_URL")
    if not url:
        log.error("DATABASE_URL no configurada")
        return 1

    issues: list[str] = []
    with psycopg2.connect(url) as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                SELECT COUNT(*) AS n FROM patients
                WHERE TRIM(display_name) = '' OR age_range IS NULL OR age_range = ''
                """
            )
            bad_patients = int(cur.fetchone()["n"])
            if bad_patients:
                issues.append(f"{bad_patients} paciente(s) con datos demográficos incompletos")

            cur.execute(
                """
                SELECT COUNT(*) AS n FROM studies s
                WHERE s.source_dataset = 'api_upload'
                  AND s.minio_object_key IS NULL
                """
            )
            no_minio = int(cur.fetchone()["n"])
            if no_minio:
                issues.append(f"{no_minio} estudio(s) API sin imagen en MinIO")

            cur.execute(
                """
                SELECT COUNT(*) AS n FROM studies s
                WHERE s.minio_object_key IS NOT NULL
                  AND NOT EXISTS (
                      SELECT 1 FROM predictions p WHERE p.study_id = s.study_id
                  )
                """
            )
            no_pred = int(cur.fetchone()["n"])
            if no_pred:
                issues.append(f"{no_pred} estudio(s) con imagen pero sin predicción")

            cur.execute(
                "SELECT COUNT(*) AS n FROM data_quality_issues WHERE detected_at > NOW() - INTERVAL '7 days'"
            )
            quality_n = int(cur.fetchone()["n"])

    if issues:
        create_alert(
            title="Registros incompletos detectados",
            message="; ".join(issues),
            severity="warning",
        )
        log.warning("Alerta creada: %s", issues)
    else:
        log.info("Auditoría OK: sin registros incompletos críticos")

    if quality_n > 0:
        log.info("Incidencias de calidad (7 días): %d", quality_n)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
