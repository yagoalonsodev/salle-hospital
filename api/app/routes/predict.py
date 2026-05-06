from flask import Blueprint, jsonify, request

from app.services import pipeline
from app.services.patients import PatientNotFoundError
from app.validators import ValidationError, validate_image_file, validate_patient_id

bp = Blueprint("predict", __name__)


@bp.post("/predict")
def predict():
    """
    Inferencia sobre imagen nueva (multipart 'file')
    o estudio existente (JSON/form 'study_id').
    """
    study_id = request.form.get("study_id") or (
        request.json.get("study_id") if request.is_json else None
    )

    if study_id:
        study_id = study_id.strip()
        if len(study_id) > 20:
            return jsonify({"error": "study_id no válido"}), 400
        try:
            result = pipeline.process_predict_existing(study_id)
            return jsonify(result)
        except LookupError as exc:
            return jsonify({"error": str(exc)}), 404
        except Exception as exc:  # noqa: BLE001
            return jsonify({"error": f"Inferencia fallida: {exc}"}), 502

    try:
        validated = validate_image_file(request.files.get("file"))
        patient_id = validate_patient_id(request.form.get("patient_id"))
    except ValidationError as exc:
        return jsonify({"error": exc.message}), exc.status_code

    try:
        result = pipeline.process_upload(validated, patient_id)
        return jsonify(result)
    except PatientNotFoundError as exc:
        return jsonify({"error": str(exc)}), 404
    except ValidationError as exc:
        return jsonify({"error": exc.message}), exc.status_code
    except Exception as exc:  # noqa: BLE001
        return jsonify({"error": f"Inferencia fallida: {exc}"}), 502
