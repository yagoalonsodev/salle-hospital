"""Persistencia de pacientes y estudios asociados."""

from __future__ import annotations

from typing import Any

from psycopg2.extras import RealDictCursor

from app.db import get_conn


def _row_to_dict(row) -> dict[str, Any]:
    d = dict(row)
    if d.get("created_at"):
        d["created_at"] = d["created_at"].isoformat()
    if d.get("captured_at"):
        d["captured_at"] = d["captured_at"].isoformat()
    if d.get("ingested_at"):
        d["ingested_at"] = d["ingested_at"].isoformat()
    if d.get("inferred_at"):
        d["inferred_at"] = d["inferred_at"].isoformat()
    return d


def list_patients() -> list[dict[str, Any]]:
    with get_conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                SELECT p.patient_id, p.display_name, p.sex, p.age_range, p.site_code,
                       si.site_name, p.created_at,
                       COUNT(s.study_id) AS study_count
                FROM patients p
                JOIN sites si ON si.site_code = p.site_code
                LEFT JOIN studies s ON s.patient_id = p.patient_id
                GROUP BY p.patient_id, p.display_name, p.sex, p.age_range,
                         p.site_code, si.site_name, p.created_at
                ORDER BY p.display_name ASC
                """
            )
            return [_row_to_dict(r) for r in cur.fetchall()]


def patient_exists(patient_id: str) -> bool:
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT 1 FROM patients WHERE patient_id = %s", (patient_id,))
            return cur.fetchone() is not None


def get_patient(patient_id: str) -> dict[str, Any] | None:
    with get_conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                SELECT p.patient_id, p.display_name, p.sex, p.age_range, p.site_code,
                       si.site_name, p.created_at
                FROM patients p
                JOIN sites si ON si.site_code = p.site_code
                WHERE p.patient_id = %s
                """,
                (patient_id,),
            )
            row = cur.fetchone()
            if not row:
                return None
            patient = _row_to_dict(row)
            cur.execute(
                """
                SELECT s.study_id, s.label, s.source_dataset, s.captured_at, s.ingested_at,
                       s.minio_object_key,
                       p2.predicted_label, p2.prediction_id, p2.inferred_at,
                       GREATEST(p2.prob_covid, p2.prob_neumonia, p2.prob_sana) AS confidence
                FROM studies s
                LEFT JOIN LATERAL (
                    SELECT predicted_label, prediction_id, inferred_at,
                           prob_covid, prob_neumonia, prob_sana
                    FROM predictions
                    WHERE study_id = s.study_id
                    ORDER BY inferred_at DESC
                    LIMIT 1
                ) p2 ON TRUE
                WHERE s.patient_id = %s
                ORDER BY s.ingested_at DESC
                """,
                (patient_id,),
            )
            patient["studies"] = [_row_to_dict(s) for s in cur.fetchall()]
            patient["study_count"] = len(patient["studies"])

            cur.execute(
                """
                SELECT prediction_id, symptoms, age, sex,
                       predicted_diagnosis::text AS predicted_diagnosis,
                       prob_json, model_name, model_version, inferred_at
                FROM clinical_predictions
                WHERE patient_id = %s
                ORDER BY inferred_at DESC
                LIMIT 50
                """,
                (patient_id,),
            )
            reports = []
            for r in cur.fetchall():
                rep = _row_to_dict(r)
                if isinstance(rep.get("prob_json"), dict):
                    rep["probabilities"] = rep["prob_json"]
                reports.append(rep)
            patient["clinical_reports"] = reports
            patient["clinical_report_count"] = len(reports)
            return patient


def create_patient(
    *,
    patient_id: str,
    display_name: str,
    sex: str,
    age_range: str,
    site_code: str,
) -> dict[str, Any]:
    with get_conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                INSERT INTO patients (patient_id, display_name, sex, age_range, site_code)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING patient_id, display_name, sex, age_range, site_code, created_at
                """,
                (patient_id, display_name, sex, age_range, site_code),
            )
            row = _row_to_dict(cur.fetchone())
            row["studies"] = []
            row["study_count"] = 0
            return row


def update_patient(
    patient_id: str,
    *,
    display_name: str | None = None,
    sex: str | None = None,
    age_range: str | None = None,
    site_code: str | None = None,
) -> dict[str, Any] | None:
    fields = []
    values: list[Any] = []
    if display_name is not None:
        fields.append("display_name = %s")
        values.append(display_name)
    if sex is not None:
        fields.append("sex = %s")
        values.append(sex)
    if age_range is not None:
        fields.append("age_range = %s")
        values.append(age_range)
    if site_code is not None:
        fields.append("site_code = %s")
        values.append(site_code)
    if not fields:
        return get_patient(patient_id)

    values.append(patient_id)
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                f"UPDATE patients SET {', '.join(fields)} WHERE patient_id = %s",
                values,
            )
            if cur.rowcount == 0:
                return None
    return get_patient(patient_id)


def list_study_keys_for_patient(patient_id: str) -> list[str]:
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT minio_object_key FROM studies
                WHERE patient_id = %s AND minio_object_key IS NOT NULL
                """,
                (patient_id,),
            )
            return [r[0] for r in cur.fetchall() if r[0]]


def delete_studies_for_patient(patient_id: str) -> int:
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM studies WHERE patient_id = %s", (patient_id,))
            return cur.rowcount


def delete_patient(patient_id: str) -> bool:
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM patients WHERE patient_id = %s", (patient_id,))
            return cur.rowcount > 0
