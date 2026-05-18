"""API REST — diagnóstico por síntomas."""

from flask import Blueprint, jsonify, request

from app.services import clinical as clinical_service
from app.services.patients import PatientNotFoundError
from app.validators import ValidationError

bp = Blueprint("clinical", __name__, url_prefix="/api/clinical")


@bp.post("/predict")
def predict_clinical():
    try:
        body = request.get_json(silent=True) or {}
        patient_id = (body.get("patient_id") or "").strip()
        if not patient_id:
            return jsonify({"error": "patient_id es obligatorio"}), 400
        result = clinical_service.predict_for_patient(patient_id, body)
        return jsonify(result), 201
    except ValidationError as exc:
        return jsonify({"error": exc.message}), exc.status_code
    except PatientNotFoundError as exc:
        return jsonify({"error": str(exc)}), 404
    except Exception as exc:  # noqa: BLE001
        msg = str(exc)
        if "Modelo clínico" in msg or "503" in msg:
            return jsonify({"error": msg}), 503
        return jsonify({"error": msg}), 500
