"""API REST de pacientes — controlador fino."""

from flask import Blueprint, jsonify, request

from app.services import patients as patient_service
from app.validators import ValidationError

bp = Blueprint("patients", __name__, url_prefix="/api/patients")


@bp.get("")
def list_patients():
    return jsonify({"patients": patient_service.list_all()})


@bp.post("")
def create_patient():
    try:
        body = request.get_json(silent=True) or {}
        patient = patient_service.create(body)
        return jsonify(patient), 201
    except ValidationError as exc:
        return jsonify({"error": exc.message}), exc.status_code
    except patient_service.PatientConflictError as exc:
        return jsonify({"error": str(exc)}), 409


@bp.get("/<patient_id>")
def get_patient(patient_id: str):
    try:
        return jsonify(patient_service.get_detail(patient_id.strip()))
    except patient_service.PatientNotFoundError as exc:
        return jsonify({"error": str(exc)}), 404


@bp.put("/<patient_id>")
@bp.patch("/<patient_id>")
def update_patient(patient_id: str):
    try:
        body = request.get_json(silent=True) or {}
        patient = patient_service.update(patient_id.strip(), body)
        return jsonify(patient)
    except ValidationError as exc:
        return jsonify({"error": exc.message}), exc.status_code
    except patient_service.PatientNotFoundError as exc:
        return jsonify({"error": str(exc)}), 404


@bp.delete("/<patient_id>")
def delete_patient(patient_id: str):
    cascade = request.args.get("cascade_studies", "false").lower() in (
        "1",
        "true",
        "yes",
    )
    try:
        result = patient_service.remove(patient_id.strip(), cascade_studies=cascade)
        return jsonify(result)
    except patient_service.PatientNotFoundError as exc:
        return jsonify({"error": str(exc)}), 404
    except patient_service.PatientConflictError as exc:
        return jsonify({"error": str(exc)}), 409
