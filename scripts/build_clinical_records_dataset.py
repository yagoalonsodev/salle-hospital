#!/usr/bin/env python3
"""Genera dataset clínico textual (~100k filas), separado de radiografías.

Salida: data/raw/clinical_records/records.csv + dataset_meta.json
"""

from __future__ import annotations

import csv
import json
import os
import random
import uuid
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "data" / "raw" / "clinical_records"
RECORDS_PATH = OUT_DIR / "records.csv"
META_PATH = OUT_DIR / "dataset_meta.json"

DEFAULT_COUNT = 100_000
SEED = 42

DIAGNOSES = (
    "sana",
    "neumonia",
    "covid",
    "gripe",
    "asma",
    "bronquitis",
    "epoc",
    "rinitis_alergica",
)

FIRST_NAMES_M = (
    "Carlos", "Miguel", "David", "Javier", "Antonio", "Pablo", "Sergio", "Álvaro",
    "Daniel", "Marcos", "Iván", "Hugo", "Diego", "Raúl", "Óscar",
)
FIRST_NAMES_F = (
    "María", "Laura", "Ana", "Carmen", "Elena", "Sofía", "Lucía", "Paula",
    "Claudia", "Marta", "Isabel", "Nuria", "Andrea", "Cristina", "Beatriz",
)
LAST_NAMES = (
    "García", "Martínez", "López", "Sánchez", "Pérez", "González", "Rodríguez",
    "Fernández", "Ruiz", "Díaz", "Moreno", "Jiménez", "Romero", "Navarro", "Torres",
)

SYMPTOM_POOLS: dict[str, tuple[str, ...]] = {
    "sana": (
        "sin síntomas respiratorios",
        "control rutinario sin quejas",
        "asintomático en revisión anual",
        "leve cansancio sin fiebre ni tos",
    ),
    "neumonia": (
        "fiebre alta tos con esputo y dolor torácico al respirar",
        "disnea escalofríos tos productiva y malestar general intenso",
        "fiebre 39°C tos seca que evoluciona a productiva sudoración nocturna",
        "dolor pleurítico fiebre tos y saturación O2 ligeramente baja",
    ),
    "covid": (
        "fiebre tos seca pérdida de olfato fatiga y cefalea",
        "fiebre mialgias tos seca anosmia desde hace 3 días",
        "tos seca fiebre diarrea leve y sensación de falta de aire leve",
        "fiebre escalofríos tos fatiga extrema y ageusia",
    ),
    "gripe": (
        "fiebre abrupta mialgias tos y dolor de garganta",
        "fiebre alta cefalea escalofríos tos y astenia marcada",
        "síntomas gripales de inicio brusco con fiebre y artralgias",
    ),
    "asma": (
        "sibilancias disnea episódica y opresión torácica con alergenos",
        "tos nocturna sibilancias y sensación de pecho cerrado",
        "disnea con esfuerzo sibilancias y uso frecuente de inhalador",
    ),
    "bronquitis": (
        "tos persistente más de 2 semanas con esputo claro",
        "tos productiva sin fiebre alta molestia torácica leve",
        "tos con expectoración irritación faríngea sin neumonía evidente",
    ),
    "epoc": (
        "disnea crónica tos matutina con esputo en fumador de larga evolución",
        "bronquitis crónica disnea de esfuerzo y sibilancias ocasionales",
        "empeoramiento de disnea tos productiva y historia de tabaquismo",
    ),
    "rinitis_alergica": (
        "estornudos rinorrea acuosa prurito nasal y lagrimeo estacional",
        "congestión nasal estornudos en racimo sin fiebre",
        "rinitis alérgica con picor ocular y nasal tras exposición a polen",
    ),
}


def _random_name(rng: random.Random, sex: str) -> str:
    if sex == "M":
        first = rng.choice(FIRST_NAMES_M)
    elif sex == "F":
        first = rng.choice(FIRST_NAMES_F)
    else:
        first = rng.choice(FIRST_NAMES_M + FIRST_NAMES_F)
    return f"{first} {rng.choice(LAST_NAMES)}"


def _symptoms_for(rng: random.Random, diagnosis: str) -> str:
    base = rng.choice(SYMPTOM_POOLS[diagnosis])
    extras = (
        "desde hace 5 días",
        "empeoramiento progresivo",
        "sin antecedentes relevantes",
        "contacto con casos similares",
        "tratamiento sintomático previo",
    )
    if diagnosis == "sana":
        return base
    return f"{base}; {rng.choice(extras)}"


def generate_rows(count: int, rng: random.Random) -> list[dict]:
    base_date = datetime(2025, 1, 1, 8, 0, 0)
    per_class = count // len(DIAGNOSES)
    remainder = count % len(DIAGNOSES)
    labels: list[str] = []
    for i, d in enumerate(DIAGNOSES):
        n = per_class + (1 if i < remainder else 0)
        labels.extend([d] * n)
    rng.shuffle(labels)

    rows: list[dict] = []
    for i, diagnosis in enumerate(labels):
        sex = rng.choices(["M", "F", "X"], weights=[48, 48, 4], k=1)[0]
        age = int(rng.triangular(4, 88, 42))
        name = _random_name(rng, sex)
        patient_ref = f"CREF-{uuid.uuid4().hex[:10]}"
        record_id = f"CR-{uuid.uuid4().hex[:12]}"
        recorded = base_date + timedelta(minutes=i * 3)
        rows.append(
            {
                "record_id": record_id,
                "patient_ref": patient_ref,
                "display_name": name,
                "age": age,
                "sex": sex,
                "symptoms": _symptoms_for(rng, diagnosis),
                "diagnosis": diagnosis,
                "recorded_at": recorded.isoformat(timespec="seconds"),
            }
        )
    return rows


def main() -> None:
    count = int(os.environ.get("RECORDS_COUNT", DEFAULT_COUNT))
    rng = random.Random(SEED)
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        "record_id",
        "patient_ref",
        "display_name",
        "age",
        "sex",
        "symptoms",
        "diagnosis",
        "recorded_at",
    ]

    rows = generate_rows(count, rng)
    with RECORDS_PATH.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)

    by_diag: dict[str, int] = {}
    for r in rows:
        by_diag[r["diagnosis"]] = by_diag.get(r["diagnosis"], 0) + 1

    meta = {
        "dataset": "clinical_records_100k",
        "rows": len(rows),
        "seed": SEED,
        "diagnoses": list(DIAGNOSES),
        "distribution": by_diag,
        "generated_at": datetime.now().astimezone().isoformat(),
        "path": str(RECORDS_PATH.relative_to(ROOT)),
        "note": "Dataset textual separado de radiografías (covid19_vs_pneumonia).",
    }
    META_PATH.write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"Registros generados: {len(rows)}")
    print("Distribución:", by_diag)
    print(f"CSV: {RECORDS_PATH}")
    print(f"Meta: {META_PATH}")


if __name__ == "__main__":
    main()
