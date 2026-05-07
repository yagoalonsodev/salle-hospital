"""Orquestación: subida → MinIO → inferencia → PostgreSQL."""

from __future__ import annotations

import logging
from typing import Any

from app import db
from app.repositories import alerts as alerts_repo
from app.services import minio_store, ml_client, patients as patient_service
from app.validators import ValidatedImage
from app.validators_patients import validate_patient_id_required

log = logging.getLogger(__name__)


def run_inference_on_image(validated: ValidatedImage) -> dict[str, Any]:
    ml_result = ml_client.predict_bytes(
        validated.raw,
        validated.filename,
        validated.content_type,
    )
    return ml_result


def persist_prediction(study_id: str, ml_result: dict[str, Any]) -> int:
    probs = ml_result["probabilities"]
    return db.save_prediction(
        study_id=study_id,
        predicted_label=ml_result["predicted_label"],
        prob_covid=probs["covid"],
        prob_neumonia=probs["neumonia"],
        prob_sana=probs["sana"],
        model_name=ml_result.get("model_name", "resnet50"),
        model_version=ml_result.get("model_version", "rx_resnet50_v1"),
    )


def process_upload(
    validated: ValidatedImage,
    patient_id: str | None,
) -> dict[str, Any]:
    pid = validate_patient_id_required(patient_id)
    patient_service.assert_exists(pid)

    study_id = db.study_id_from_bytes(validated.raw)
    ext = "." + validated.filename.rsplit(".", 1)[-1].lower()
    if ext not in (".jpg", ".jpeg", ".png"):
        ext = ".jpg"
    obj_key = minio_store.object_key_for_study(study_id, ext if ext != ".jpeg" else ".jpg")
    minio_store.upload_bytes(obj_key, validated.raw, validated.content_type)
    file_path = f"api://{obj_key}"
    db.upsert_study(
        study_id=study_id,
        patient_id=pid,
        file_path=file_path,
        minio_object_key=obj_key,
    )

    try:
        ml_result = run_inference_on_image(validated)
    except Exception as exc:
        log.exception("Inferencia fallida study_id=%s", study_id)
        alerts_repo.create_alert(
            title="Error de inferencia",
            message=f"Estudio {study_id}: {exc}",
            severity="critical",
        )
        raise

    prediction_id = persist_prediction(study_id, ml_result)
    log.info(
        "Upload OK study_id=%s label=%s",
        study_id,
        ml_result.get("predicted_label"),
    )

    return {
        "study_id": study_id,
        "patient_id": pid,
        "prediction_id": prediction_id,
        "minio_object_key": obj_key,
        **ml_result,
    }


def process_predict_existing(study_id: str) -> dict[str, Any]:
    study = db.get_study(study_id)
    if not study:
        raise LookupError(f"Estudio no encontrado: {study_id}")
    key = study.get("minio_object_key")
    if not key:
        raise LookupError(f"El estudio {study_id} no tiene imagen en MinIO")
    raw = minio_store.download_bytes(key)
    filename = key.rsplit("/", 1)[-1]
    content_type = "image/jpeg"
    ml_result = ml_client.predict_bytes(raw, filename, content_type)
    prediction_id = persist_prediction(study_id, ml_result)
    return {
        "study_id": study_id,
        "prediction_id": prediction_id,
        **ml_result,
    }
