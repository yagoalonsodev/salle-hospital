"""Datos agregados para el dashboard Streamlit."""

from flask import Blueprint, jsonify

from app import db
from app.config import MODEL_VERSION
from app.repositories import alerts as alerts_repo
from app.repositories import dashboard as dash_repo
from app.services import minio_store, ml_client

bp = Blueprint("dashboard", __name__, url_prefix="/api")


@bp.get("/dashboard")
def dashboard_data():
    db_ok, db_err = db.check_db()
    minio_ok, minio_err = minio_store.check_minio()
    ml_ok, ml_err, ml_info = ml_client.check_ml()
    payload = dash_repo.build_dashboard_payload()
    payload.setdefault("metrics", {})["model_version"] = MODEL_VERSION
    payload["health"] = {
        "status": "ok" if (db_ok and minio_ok and ml_ok) else "degraded",
        "checks": {
            "database": {"ok": db_ok, "error": db_err},
            "minio": {"ok": minio_ok, "error": minio_err},
            "ml": {"ok": ml_ok, "error": ml_err, "info": ml_info},
        },
    }
    payload["alerts"] = alerts_repo.list_alerts(limit=50)
    return jsonify(payload)


@bp.patch("/alerts/<int:alert_id>/ack")
def acknowledge_alert(alert_id: int):
    if alerts_repo.acknowledge_alert(alert_id):
        return jsonify({"acknowledged": True, "alert_id": alert_id})
    return jsonify({"error": "Alerta no encontrada"}), 404
