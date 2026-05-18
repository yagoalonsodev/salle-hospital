"""Logs centralizados (MongoDB) para dashboard y operaciones."""

from flask import Blueprint, jsonify, request

from app.repositories import logs_mongo

bp = Blueprint("logs", __name__, url_prefix="/api")


@bp.get("/logs")
def list_logs():
    collection = request.args.get("collection", "application_logs")
    if collection not in ("application_logs", "airflow_logs", "file_logs"):
        return jsonify({"error": "collection inválida"}), 400
    service = request.args.get("service") or None
    level = request.args.get("level") or None
    try:
        limit = int(request.args.get("limit", "100"))
    except ValueError:
        limit = 100
    rows = logs_mongo.fetch_logs(
        collection,
        service=service,
        level=level,
        limit=limit,
    )
    return jsonify(
        {
            "collection": collection,
            "count": len(rows),
            "items": rows,
        }
    )
