"""Validación de payloads de pacientes."""

from __future__ import annotations

import re
import secrets
from typing import Any

from app.repositories import sites as sites_repo
from app.validators import PATIENT_ID_RE, ValidationError

VALID_SEX = frozenset({"M", "F", "X"})


def generate_patient_id() -> str:
    return f"PAT-{secrets.token_hex(4).upper()}"


def validate_patient_id_required(patient_id: str | None) -> str:
    if not patient_id or not str(patient_id).strip():
        raise ValidationError("patient_id es obligatorio")
    patient_id = str(patient_id).strip()
    if len(patient_id) > 16:
        raise ValidationError("patient_id demasiado largo")
    if not PATIENT_ID_RE.match(patient_id):
        raise ValidationError("patient_id debe tener formato PAT-xxxxxxxx")
    return patient_id


def validate_patient_body(data: dict[str, Any] | None, *, partial: bool = False) -> dict[str, Any]:
    if not data or not isinstance(data, dict):
        raise ValidationError("Cuerpo JSON inválido")

    out: dict[str, Any] = {}

    if "display_name" in data or not partial:
        name = str(data.get("display_name", "")).strip()
        if not name:
            raise ValidationError("display_name es obligatorio")
        if len(name) > 80:
            raise ValidationError("display_name demasiado largo (máx. 80)")
        out["display_name"] = name

    if "patient_id" in data or not partial:
        raw_id = data.get("patient_id")
        if raw_id is None or str(raw_id).strip() == "":
            if partial:
                pass
            else:
                out["patient_id"] = generate_patient_id()
        else:
            out["patient_id"] = validate_patient_id_required(str(raw_id))

    if "sex" in data or not partial:
        sex = str(data.get("sex", "X")).strip().upper()
        if sex not in VALID_SEX:
            raise ValidationError("sex debe ser M, F o X")
        out["sex"] = sex

    if "age_range" in data or not partial:
        age = str(data.get("age_range", "")).strip()
        if not age or len(age) > 10:
            raise ValidationError("age_range es obligatorio (máx. 10 caracteres)")
        out["age_range"] = age

    if "site_code" in data or not partial:
        site = str(data.get("site_code", "")).strip()
        if not site or len(site) > 16:
            raise ValidationError("site_code es obligatorio")
        if not sites_repo.exists(site):
            raise ValidationError("Centro no registrado en el sistema")
        out["site_code"] = site

    if partial and not out:
        raise ValidationError("No hay campos para actualizar")

    return out
