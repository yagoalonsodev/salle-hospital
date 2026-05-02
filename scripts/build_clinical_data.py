#!/usr/bin/env python3
"""Genera CSV clínico simulado y manifest desde data/raw/covid19_vs_pneumonia."""

from __future__ import annotations

import csv
import hashlib
import random
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW_IMAGES = ROOT / "data" / "raw" / "covid19_vs_pneumonia"
CLINICAL_DIR = ROOT / "data" / "raw" / "clinical"
MANIFEST_PATH = RAW_IMAGES / "manifest.csv"

LABEL_MAP = {
    "NORMAL": "sana",
    "PNEUMONIA": "neumonia",
    "COVID19": "covid",
}

SEXES = ("M", "F", "X")
AGE_RANGES = ("18-30", "31-45", "46-60", "61-75", "76+")


def iter_images() -> list[dict]:
    rows: list[dict] = []
    for split_dir in sorted(RAW_IMAGES.iterdir()):
        if not split_dir.is_dir() or split_dir.name.startswith("."):
            continue
        split = split_dir.name
        for class_dir in sorted(split_dir.iterdir()):
            if not class_dir.is_dir():
                continue
            folder = class_dir.name
            label = LABEL_MAP.get(folder)
            if not label:
                continue
            for img in sorted(class_dir.glob("*.jpg")):
                rel = img.relative_to(ROOT).as_posix()
                rows.append(
                    {
                        "file_path": rel,
                        "split": split,
                        "folder": folder,
                        "label": label,
                        "filename": img.name,
                    }
                )
    return rows


def stable_patient_id(file_path: str) -> str:
    h = hashlib.sha256(file_path.encode()).hexdigest()[:10]
    return f"PAT-{h}"


def main() -> None:
    if not RAW_IMAGES.is_dir():
        raise SystemExit(f"No existe {RAW_IMAGES}. Mueve el dataset ahí primero.")

    images = iter_images()
    if not images:
        raise SystemExit(f"No se encontraron imágenes en {RAW_IMAGES}")

    CLINICAL_DIR.mkdir(parents=True, exist_ok=True)
    base_date = datetime(2026, 4, 1, 8, 0, 0)
    rng = random.Random(42)

    patients: dict[str, dict] = {}
    studies: list[dict] = []

    for i, img in enumerate(images):
        pid = stable_patient_id(img["file_path"])
        if pid not in patients:
            patients[pid] = {
                "patient_id": pid,
                "sex": rng.choice(SEXES),
                "age_range": rng.choice(AGE_RANGES),
                "site_code": "LSHC-01",
            }
        study_id = f"STU-{hashlib.md5(img['file_path'].encode()).hexdigest()[:12]}"
        studies.append(
            {
                "study_id": study_id,
                "patient_id": pid,
                "file_path": img["file_path"],
                "split": img["split"],
                "label": img["label"],
                "source_dataset": "covid19_vs_pneumonia",
                "modality": "CR",
                "body_part": "chest",
                "captured_at": (base_date + timedelta(hours=i % 720)).isoformat(
                    timespec="seconds"
                ),
            }
        )

    with MANIFEST_PATH.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(
            f,
            fieldnames=["file_path", "split", "folder", "label", "filename"],
        )
        w.writeheader()
        w.writerows(images)

    with (CLINICAL_DIR / "patients.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(
            f,
            fieldnames=["patient_id", "sex", "age_range", "site_code"],
        )
        w.writeheader()
        w.writerows(sorted(patients.values(), key=lambda r: r["patient_id"]))

    with (CLINICAL_DIR / "studies.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(
            f,
            fieldnames=[
                "study_id",
                "patient_id",
                "file_path",
                "split",
                "label",
                "source_dataset",
                "modality",
                "body_part",
                "captured_at",
            ],
        )
        w.writeheader()
        w.writerows(studies)

    events = [
        {
            "event_id": "EVT-001",
            "run_id": "RUN-20260401-INGEST",
            "stage": "ingesta",
            "status": "ok",
            "records": len(images),
            "message": "Manifest RX generado desde data/raw/covid19_vs_pneumonia",
            "logged_at": datetime(2026, 4, 1, 9, 0, 0).isoformat(),
        },
        {
            "event_id": "EVT-002",
            "run_id": "RUN-20260401-INGEST",
            "stage": "validacion",
            "status": "ok",
            "records": len(images),
            "message": "6432 imágenes; 3 clases (sana, neumonia, covid)",
            "logged_at": datetime(2026, 4, 1, 9, 5, 0).isoformat(),
        },
    ]
    with (CLINICAL_DIR / "pipeline_events.csv").open(
        "w", newline="", encoding="utf-8"
    ) as f:
        w = csv.DictWriter(
            f,
            fieldnames=[
                "event_id",
                "run_id",
                "stage",
                "status",
                "records",
                "message",
                "logged_at",
            ],
        )
        w.writeheader()
        w.writerows(events)

    by_label: dict[str, int] = {}
    for img in images:
        by_label[img["label"]] = by_label.get(img["label"], 0) + 1

    print(f"Imágenes: {len(images)}")
    print(f"Pacientes simulados: {len(patients)}")
    print(f"Estudios: {len(studies)}")
    print("Por etiqueta:", by_label)
    print(f"Manifest: {MANIFEST_PATH}")
    print(f"CSV clínico: {CLINICAL_DIR}")


if __name__ == "__main__":
    main()
