"""Acceso a PostgreSQL."""

from __future__ import annotations

import hashlib
from contextlib import contextmanager
from datetime import datetime, timezone
from typing import Any, Generator

import psycopg2
from psycopg2.extras import RealDictCursor

from app.config import MODEL_VERSION, database_url


@contextmanager
def get_conn() -> Generator:
    conn = psycopg2.connect(database_url())
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def check_db() -> tuple[bool, str | None]:
    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
        return True, None
    except Exception as exc:  # noqa: BLE001
        return False, str(exc)


def upsert_study(
    *,
    study_id: str,
    patient_id: str,
    file_path: str,
    minio_object_key: str,
) -> None:
    """Registra estudio clínico (sin ground truth; la predicción va en predictions)."""
    now = datetime.now(timezone.utc)
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO studies (
                    study_id, patient_id, file_path, minio_object_key,
                    split, label, source_dataset, captured_at
                ) VALUES (
                    %s, %s, %s, %s, 'clinical', NULL, 'api_upload', %s
                )
                ON CONFLICT (study_id) DO UPDATE SET
                    minio_object_key = EXCLUDED.minio_object_key,
                    ingested_at = NOW()
                """,
                (study_id, patient_id, file_path, minio_object_key, now),
            )


def get_study(study_id: str) -> dict[str, Any] | None:
    with get_conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                SELECT study_id, patient_id, file_path, minio_object_key, label
                FROM studies WHERE study_id = %s
                """,
                (study_id,),
            )
            row = cur.fetchone()
            return dict(row) if row else None


def save_prediction(
    *,
    study_id: str,
    predicted_label: str,
    prob_covid: float,
    prob_neumonia: float,
    prob_sana: float,
    model_name: str,
    model_version: str,
) -> int:
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO predictions (
                    study_id, predicted_label,
                    prob_sana, prob_neumonia, prob_covid,
                    model_name, model_version
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING prediction_id
                """,
                (
                    study_id,
                    predicted_label,
                    prob_sana,
                    prob_neumonia,
                    prob_covid,
                    model_name,
                    model_version,
                ),
            )
            return int(cur.fetchone()[0])


def fetch_metrics() -> dict[str, Any]:
    with get_conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT COUNT(*) AS total FROM predictions")
            total = int(cur.fetchone()["total"])

            cur.execute(
                """
                SELECT predicted_label, COUNT(*) AS count
                FROM predictions
                GROUP BY predicted_label
                ORDER BY count DESC
                """
            )
            by_label = [dict(r) for r in cur.fetchall()]

            cur.execute(
                """
                SELECT p.prediction_id, p.study_id, p.predicted_label,
                       p.prob_sana, p.prob_neumonia, p.prob_covid, p.inferred_at,
                       pt.display_name AS patient_name, pt.patient_id,
                       GREATEST(p.prob_covid, p.prob_neumonia, p.prob_sana) AS confidence
                FROM predictions p
                JOIN studies s ON s.study_id = p.study_id
                JOIN patients pt ON pt.patient_id = s.patient_id
                WHERE s.source_dataset = 'api_upload'
                ORDER BY p.inferred_at DESC
                LIMIT 100
                """
            )
            recent = []
            for r in cur.fetchall():
                row = dict(r)
                if row.get("inferred_at"):
                    row["inferred_at"] = row["inferred_at"].isoformat()
                recent.append(row)

            cur.execute("SELECT COUNT(*) AS n FROM studies WHERE source_dataset = 'api_upload'")
            api_uploads = int(cur.fetchone()["n"])

            cur.execute("SELECT COUNT(*) AS n FROM patients")
            patients_total = int(cur.fetchone()["n"])

    return {
        "predictions_total": total,
        "predictions_by_label": by_label,
        "api_uploads": api_uploads,
        "patients_total": patients_total,
        "recent_predictions": recent,
    }


def study_id_from_bytes(raw: bytes) -> str:
    return f"STU-{hashlib.md5(raw).hexdigest()[:12].upper()}"
