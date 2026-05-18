"""Consultas agregadas para el dashboard."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from psycopg2.extras import RealDictCursor

from app.db import get_conn, fetch_metrics


def _iso_rows(rows: list[dict]) -> list[dict]:
    out = []
    for r in rows:
        d = dict(r)
        for k, v in d.items():
            if hasattr(v, "isoformat"):
                d[k] = v.isoformat()
        out.append(d)
    return out


def fetch_pipeline_summary() -> dict[str, int]:
    """Resumen compacto de pipeline (detalle de logs en MongoDB)."""
    with get_conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                SELECT status, COUNT(*) AS count
                FROM pipeline_runs
                GROUP BY status
                """
            )
            rows = {str(r["status"]): int(r["count"]) for r in cur.fetchall()}
    return {
        "ok": rows.get("ok", 0),
        "running": rows.get("running", 0),
        "failed": rows.get("failed", 0),
    }


def fetch_recent_studies(limit: int = 24) -> list[dict[str, Any]]:
    with get_conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                SELECT s.study_id, s.source_dataset, s.ingested_at, s.minio_object_key,
                       p.predicted_label,
                       GREATEST(p.prob_covid, p.prob_neumonia, p.prob_sana) AS confidence,
                       pt.display_name AS patient_name
                FROM studies s
                LEFT JOIN LATERAL (
                    SELECT predicted_label, prob_covid, prob_neumonia, prob_sana
                    FROM predictions WHERE study_id = s.study_id
                    ORDER BY inferred_at DESC LIMIT 1
                ) p ON TRUE
                LEFT JOIN patients pt ON pt.patient_id = s.patient_id
                WHERE s.minio_object_key IS NOT NULL
                ORDER BY s.ingested_at DESC
                LIMIT %s
                """,
                (limit,),
            )
            return _iso_rows([dict(r) for r in cur.fetchall()])


def load_ml_evaluation() -> dict[str, Any] | None:
    path = os.environ.get(
        "ML_REPORT_PATH",
        "/app/ml_reports/training_report_v1.json",
    )
    p = Path(path)
    if not p.is_file():
        alt = Path(__file__).resolve().parents[3] / "ml/models/reports/training_report_v1.json"
        p = alt if alt.is_file() else p
    if not p.is_file():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def build_dashboard_payload() -> dict[str, Any]:
    metrics = fetch_metrics()
    total_pred = metrics.get("predictions_total") or 0
    by_label = metrics.get("predictions_by_label") or []
    pct = []
    for row in by_label:
        count = int(row.get("count") or 0)
        pct.append(
            {
                "label": row["predicted_label"],
                "count": count,
                "percent": round(100.0 * count / total_pred, 1) if total_pred else 0,
            }
        )

    ml_eval = load_ml_evaluation()
    errors = None
    if ml_eval and ml_eval.get("metrics_by_split", {}).get("test"):
        test = ml_eval["metrics_by_split"]["test"]
        cm = test.get("confusion_matrix")
        labels = test.get("labels") or ["covid", "neumonia", "sana"]
        fn_neumonia_sana = 0
        if cm and len(cm) >= 2 and len(cm[1]) >= 3:
            fn_neumonia_sana = int(cm[1][2])
        off_diag = 0
        if cm:
            for i, row in enumerate(cm):
                for j, v in enumerate(row):
                    if i != j:
                        off_diag += int(v)
        errors = {
            "accuracy_test": test.get("accuracy"),
            "f1_macro_test": test.get("f1_macro"),
            "fn_neumonia_to_sana": fn_neumonia_sana,
            "misclassified_total": off_diag,
            "confusion_matrix": cm,
            "labels": labels,
        }

    return {
        "metrics": metrics,
        "predictions_by_class": pct,
        "pipeline_summary": fetch_pipeline_summary(),
        "recent_studies": fetch_recent_studies(),
        "ml_evaluation": errors,
    }
