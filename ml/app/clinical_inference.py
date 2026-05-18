"""Inferencia modelo clínico (síntomas → diagnóstico)."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import joblib

_MODEL_BUNDLE: dict[str, Any] | None = None
_LOAD_ERROR: str | None = None


def _model_path() -> Path:
    raw = os.environ.get("CLINICAL_MODEL_PATH", "models/clinical_symptoms_v1.joblib")
    p = Path(raw)
    if not p.is_absolute():
        p = Path(__file__).resolve().parents[1] / p
    return p


def load_clinical_model() -> None:
    global _MODEL_BUNDLE, _LOAD_ERROR
    path = _model_path()
    if not path.is_file():
        _LOAD_ERROR = f"No se encontró modelo clínico en {path}"
        _MODEL_BUNDLE = None
        return
    try:
        _MODEL_BUNDLE = joblib.load(path)
        _LOAD_ERROR = None
    except Exception as exc:  # noqa: BLE001
        _MODEL_BUNDLE = None
        _LOAD_ERROR = str(exc)


def clinical_model_status() -> dict[str, Any]:
    if _MODEL_BUNDLE is None and _LOAD_ERROR is None:
        load_clinical_model()
    return {
        "clinical_model_loaded": _MODEL_BUNDLE is not None,
        "clinical_model_path": str(_model_path()),
        "clinical_model_version": (
            _MODEL_BUNDLE.get("version") if _MODEL_BUNDLE else None
        ),
        "clinical_load_error": _LOAD_ERROR,
        "clinical_labels": _MODEL_BUNDLE.get("labels") if _MODEL_BUNDLE else [],
    }


def predict_clinical(*, symptoms: str, age: int, sex: str) -> dict[str, Any]:
    if _MODEL_BUNDLE is None:
        load_clinical_model()
    if _MODEL_BUNDLE is None:
        raise FileNotFoundError(_LOAD_ERROR or "Modelo clínico no cargado")

    symptoms = (symptoms or "").strip()
    if len(symptoms) < 3:
        raise ValueError("Los síntomas deben tener al menos 3 caracteres")

    sex_norm = (sex or "X").strip().upper()[:1]
    if sex_norm not in ("M", "F", "X"):
        sex_norm = "X"

    age = max(0, min(120, int(age)))

    pipe = _MODEL_BUNDLE["pipeline"]
    labels: list[str] = _MODEL_BUNDLE["labels"]
    import pandas as pd

    row = pd.DataFrame([{"symptoms": symptoms, "age": age, "sex": sex_norm}])
    pred = pipe.predict(row)[0]
    proba = pipe.predict_proba(row)[0]
    probs = {label: float(p) for label, p in zip(pipe.classes_, proba, strict=True)}

    return {
        "predicted_diagnosis": str(pred),
        "probabilities": probs,
        "model_name": "clinical_symptoms_logreg",
        "model_version": _MODEL_BUNDLE.get("version", "clinical_symptoms_v1"),
        "labels": labels,
    }
