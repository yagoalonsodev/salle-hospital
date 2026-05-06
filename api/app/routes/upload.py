from flask import Blueprint, jsonify, request

from app.services import pipeline
from app.services.patients import PatientNotFoundError
from app.validators import ValidationError, validate_image_file, validate_patient_id

bp = Blueprint("upload", __name__)


@bp.post("/upload")
def upload():
    """Sube radiografía, ejecuta inferencia automática y guarda en PostgreSQL."""
    try:
        validated = validate_image_file(request.files.get("file"))
        patient_id = validate_patient_id(request.form.get("patient_id"))
    except ValidationError as exc:
        return jsonify({"error": exc.message}), exc.status_code

    try:
        result = pipeline.process_upload(validated, patient_id)
        return jsonify(result), 201
    except PatientNotFoundError as exc:
        return jsonify({"error": str(exc)}), 404
    except ValidationError as exc:
        return jsonify({"error": exc.message}), exc.status_code
    except Exception as exc:  # noqa: BLE001
        return jsonify({"error": f"Error al procesar la imagen: {exc}"}), 502
