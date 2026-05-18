"""Casos de uso: predicción clínica por síntomas."""

from __future__ import annotations

from typing import Any

from app.repositories import clinical as clinical_repo
from app.services import ml_client, patients as patient_service
from app.validators import ValidationError


def _parse_age(age_range: str | None, age: int | None) -> int:
    if age is not None:
        return max(0, min(120, int(age)))
    if not age_range:
        return 40
    s = str(age_range).strip()
    if "-" in s:
        parts = s.split("-", 1)
        try:
            lo, hi = int(parts[0]), int(parts[1].replace("+", ""))
            return (lo + hi) // 2
        except ValueError:
            pass
    digits = "".join(c for c in s if c.isdigit())
    if digits:
        return max(0, min(120, int(digits[:3])))
    return 40


def predict_for_patient(patient_id: str, body: dict[str, Any]) -> dict[str, Any]:
    patient_id = patient_id.strip()
    patient_service.assert_exists(patient_id)

    symptoms = (body.get("symptoms") or "").strip()
    if len(symptoms) < 3:
        raise ValidationError("Los síntomas deben tener al menos 3 caracteres", 400)

    patient = patient_service.get_detail(patient_id)
    sex = (body.get("sex") or patient.get("sex") or "X").strip().upper()[:1]
    if sex not in ("M", "F", "X"):
        sex = "X"

    age = _parse_age(patient.get("age_range"), body.get("age"))

    ml_result = ml_client.predict_clinical(symptoms=symptoms, age=age, sex=sex)

    saved = clinical_repo.insert_prediction(
        patient_id=patient_id,
        symptoms=symptoms,
        age=age,
        sex=sex,
        predicted_diagnosis=ml_result["predicted_diagnosis"],
        prob_json=ml_result.get("probabilities") or {},
        model_name=ml_result.get("model_name", "clinical_symptoms_logreg"),
        model_version=ml_result.get("model_version", "clinical_symptoms_v1"),
    )

    return {
        **saved,
        "probabilities": ml_result.get("probabilities"),
        "labels": ml_result.get("labels"),
        "patient_display_name": patient.get("display_name"),
    }
