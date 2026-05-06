"""Imágenes de estudios almacenados en MinIO."""

from flask import Blueprint, Response, jsonify

from app import db
from app.services import minio_store

bp = Blueprint("studies", __name__, url_prefix="/api/studies")


@bp.get("/<study_id>/image")
def study_image(study_id: str):
    study = db.get_study(study_id.strip())
    if not study:
        return jsonify({"error": "Estudio no encontrado"}), 404
    key = study.get("minio_object_key")
    if not key:
        return jsonify({"error": "Imagen no disponible"}), 404
    try:
        raw = minio_store.download_bytes(key)
    except Exception as exc:  # noqa: BLE001
        return jsonify({"error": f"No se pudo leer la imagen: {exc}"}), 502
    content_type = "image/png" if key.lower().endswith(".png") else "image/jpeg"
    return Response(raw, mimetype=content_type)
