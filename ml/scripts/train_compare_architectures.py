#!/usr/bin/env python3
"""Entrena (o reutiliza) los 4 candidatos y genera architecture_comparison.json."""

from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from training_core import (  # noqa: E402
    ModelSpec,
    load_report,
    report_to_comparison_entry,
    run_training,
    write_architecture_comparison,
)
from models.architectures import (  # noqa: E402
    build_baseline_cnn,
    build_transfer_classifier,
)

SPECS: list[ModelSpec] = [
    ModelSpec(
        arch_id="baseline_cnn",
        model_version="rx_baseline_cnn_v1",
        build_model=build_baseline_cnn,
        finetune=False,
    ),
    ModelSpec(
        arch_id="resnet50",
        model_version="rx_resnet50_v1",
        build_model=lambda: build_transfer_classifier("resnet50", trainable_backbone=False),
        finetune=True,
        finetune_layers=int(os.environ.get("FINETUNE_LAYERS", "40")),
        legacy_reports=True,
    ),
    ModelSpec(
        arch_id="efficientnetb0",
        model_version="rx_efficientnetb0_v1",
        build_model=lambda: build_transfer_classifier("efficientnetb0", trainable_backbone=False),
        finetune=True,
        finetune_layers=int(os.environ.get("FINETUNE_LAYERS_EFFICIENTNET", "30")),
    ),
    ModelSpec(
        arch_id="densenet121",
        model_version="rx_densenet121_v1",
        build_model=lambda: build_transfer_classifier("densenet121", trainable_backbone=False),
        finetune=True,
        finetune_layers=int(os.environ.get("FINETUNE_LAYERS_DENSENET", "40")),
    ),
]

SCRIPT_BY_ARCH = {
    "baseline_cnn": "train_baseline_cnn.py",
    "resnet50": "train_resnet50.py",
    "efficientnetb0": "train_efficientnetb0.py",
    "densenet121": "train_densenet121.py",
}


def _selected_archs() -> list[str]:
    raw = os.environ.get("COMPARE_ARCHS", "").strip()
    if not raw:
        return [s.arch_id for s in SPECS]
    return [a.strip() for a in raw.split(",") if a.strip()]


def main() -> None:
    only_aggregate = os.environ.get("AGGREGATE_ONLY", "0") == "1"
    reuse_existing = os.environ.get("REUSE_EXISTING", "1") == "1"
    selected = _selected_archs()
    spec_by_id = {s.arch_id: s for s in SPECS}

    entries: dict[str, dict] = {}
    for arch_id in selected:
        if arch_id not in spec_by_id:
            raise SystemExit(f"Arquitectura desconocida: {arch_id}")
        spec = spec_by_id[arch_id]

        if only_aggregate:
            report = load_report(spec)
        elif reuse_existing and spec.report_json.is_file():
            print(f"[{arch_id}] Reutilizando {spec.report_json}", flush=True)
            report = load_report(spec)
        else:
            report = run_training(spec)

        report.setdefault("arch_id", arch_id)
        entries[arch_id] = report_to_comparison_entry(report)

    out = write_architecture_comparison(entries)
    print(f"\nComparativa guardada: {out}", flush=True)
    payload = out.read_text(encoding="utf-8")
    import json

    data = json.loads(payload)
    print("Ranking:", " > ".join(data["ranking_test_f1_macro"]), flush=True)
    print(f"Ganador métricas: {data['recommended']}", flush=True)
    print(f"Modelo producción (fijado): {data['production_model']}", flush=True)


if __name__ == "__main__":
    main()
