from flask import Blueprint, jsonify

from app import db
from app.config import MODEL_VERSION
from app.services import ml_client

bp = Blueprint("metrics", __name__)


@bp.get("/metrics")
def metrics():
    data = db.fetch_metrics()
    _, _, ml_info = ml_client.check_ml()
    return jsonify(
        {
            "service": "api",
            "model_version": MODEL_VERSION,
            "ml_service": ml_info,
            **data,
        }
    )
