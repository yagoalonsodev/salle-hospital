from flask import Blueprint, jsonify

from app import db
from app.services import minio_store, ml_client

bp = Blueprint("health", __name__)


@bp.get("/health")
def health():
    db_ok, db_err = db.check_db()
    minio_ok, minio_err = minio_store.check_minio()
    ml_ok, ml_err, ml_info = ml_client.check_ml()

    checks = {
        "database": {"ok": db_ok, "error": db_err},
        "minio": {"ok": minio_ok, "error": minio_err},
        "ml": {"ok": ml_ok, "error": ml_err, "info": ml_info},
    }
    all_ok = db_ok and minio_ok and ml_ok
    status = "ok" if all_ok else "degraded"
    code = 200 if db_ok else 503

    return jsonify({"status": status, "service": "api", "checks": checks}), code
