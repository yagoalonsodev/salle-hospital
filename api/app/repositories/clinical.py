"""Persistencia: registros clínicos e inferencias por síntomas."""

from __future__ import annotations

import json
from typing import Any

from psycopg2.extras import RealDictCursor, Json

from app.db import get_conn


def _row_to_dict(row) -> dict[str, Any]:
    d = dict(row)
    for key in ("recorded_at", "ingested_at", "inferred_at"):
        if d.get(key):
            d[key] = d[key].isoformat()
    if d.get("prob_json") and isinstance(d["prob_json"], str):
        d["prob_json"] = json.loads(d["prob_json"])
    return d


def list_reports_for_patient(patient_id: str) -> list[dict[str, Any]]:
    with get_conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                SELECT prediction_id, patient_id, record_id, symptoms, age, sex,
                       predicted_diagnosis::text AS predicted_diagnosis,
                       prob_json, model_name, model_version, inferred_at
                FROM clinical_predictions
                WHERE patient_id = %s
                ORDER BY inferred_at DESC
                LIMIT 50
                """,
                (patient_id,),
            )
            return [_row_to_dict(r) for r in cur.fetchall()]


def insert_prediction(
    *,
    patient_id: str,
    symptoms: str,
    age: int | None,
    sex: str | None,
    predicted_diagnosis: str,
    prob_json: dict[str, float],
    model_name: str,
    model_version: str,
    record_id: str | None = None,
) -> dict[str, Any]:
    with get_conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                INSERT INTO clinical_predictions (
                    patient_id, record_id, symptoms, age, sex,
                    predicted_diagnosis, prob_json, model_name, model_version
                )
                VALUES (%s, %s, %s, %s, %s, %s::clinical_diagnosis, %s, %s, %s)
                RETURNING prediction_id, patient_id, record_id, symptoms, age, sex,
                          predicted_diagnosis::text AS predicted_diagnosis,
                          prob_json, model_name, model_version, inferred_at
                """,
                (
                    patient_id,
                    record_id,
                    symptoms,
                    age,
                    sex,
                    predicted_diagnosis,
                    Json(prob_json),
                    model_name,
                    model_version,
                ),
            )
            return _row_to_dict(cur.fetchone())
