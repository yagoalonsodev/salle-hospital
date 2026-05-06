"""Casos de uso: pacientes (0..N radiografías)."""

from __future__ import annotations

from typing import Any

from app.repositories import patients as repo
from app.services import minio_store
from app.validators_patients import validate_patient_body


class PatientNotFoundError(LookupError):
    pass


class PatientConflictError(ValueError):
    pass


def list_all() -> list[dict[str, Any]]:
    return repo.list_patients()


def get_detail(patient_id: str) -> dict[str, Any]:
    patient = repo.get_patient(patient_id)
    if not patient:
        raise PatientNotFoundError(f"Paciente no encontrado: {patient_id}")
    return patient


def create(data: dict[str, Any]) -> dict[str, Any]:
    payload = validate_patient_body(data, partial=False)
    pid = payload["patient_id"]
    if repo.patient_exists(pid):
        raise PatientConflictError(f"Ya existe el paciente {pid}")
    return repo.create_patient(
        patient_id=pid,
        display_name=payload["display_name"],
        sex=payload["sex"],
        age_range=payload["age_range"],
        site_code=payload["site_code"],
    )


def update(patient_id: str, data: dict[str, Any]) -> dict[str, Any]:
    if not repo.patient_exists(patient_id):
        raise PatientNotFoundError(f"Paciente no encontrado: {patient_id}")
    payload = validate_patient_body(data, partial=True)
    updated = repo.update_patient(
        patient_id,
        display_name=payload.get("display_name"),
        sex=payload.get("sex"),
        age_range=payload.get("age_range"),
        site_code=payload.get("site_code"),
    )
    if not updated:
        raise PatientNotFoundError(f"Paciente no encontrado: {patient_id}")
    return updated


def remove(patient_id: str, *, cascade_studies: bool = False) -> dict[str, Any]:
    if not repo.patient_exists(patient_id):
        raise PatientNotFoundError(f"Paciente no encontrado: {patient_id}")

    patient = repo.get_patient(patient_id)
    study_count = patient["study_count"] if patient else 0

    if study_count > 0 and not cascade_studies:
        raise PatientConflictError(
            f"El paciente tiene {study_count} radiografía(s). "
            "Use cascade_studies=true para eliminar también los estudios."
        )

    deleted_studies = 0
    if study_count > 0:
        keys = repo.list_study_keys_for_patient(patient_id)
        for key in keys:
            try:
                minio_store.delete_object(key)
            except Exception:
                pass
        deleted_studies = repo.delete_studies_for_patient(patient_id)

    if not repo.delete_patient(patient_id):
        raise PatientNotFoundError(f"Paciente no encontrado: {patient_id}")

    return {
        "deleted": True,
        "patient_id": patient_id,
        "studies_deleted": deleted_studies,
    }


def assert_exists(patient_id: str) -> None:
    if not repo.patient_exists(patient_id):
        raise PatientNotFoundError(
            f"Paciente {patient_id} no existe. Créelo antes de asociar radiografías."
        )
