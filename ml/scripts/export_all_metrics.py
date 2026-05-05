#!/usr/bin/env python3
"""Regenera métricas completas (train / val / test) desde .h5 o mejor checkpoint."""

from __future__ import annotations

import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

import tensorflow as tf

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from train_resnet50 import (  # noqa: E402
    CHECKPOINT_DIR,
    MODELS_DIR,
    REPORTS_DIR,
    _configure_tf,
    _evaluate_all_splits,
    _plot_confusion_matrix,
)
import numpy as np
from tensorflow import keras


def _load_model() -> tuple[keras.Model, str]:
    h5 = MODELS_DIR / "rx_resnet50_v1.h5"
    if h5.is_file():
        return keras.models.load_model(h5, compile=False), h5.name
    pattern = re.compile(r"val([0-9.]+)\.keras$")
    best_path, best_val = None, -1.0
    for path in CHECKPOINT_DIR.glob("rx_resnet50_v1_*.keras"):
        m = pattern.search(path.name)
        if m and float(m.group(1)) > best_val:
            best_val = float(m.group(1))
            best_path = path
    if best_path is None:
        raise FileNotFoundError("No hay modelo .h5 ni checkpoints")
    return keras.models.load_model(best_path, compile=False), best_path.name


def _write_markdown(all_metrics: dict, path: Path) -> None:
    lines = ["# Métricas rx_resnet50_v1\n\n"]
    for split in ("train", "validation", "test"):
        m = all_metrics[split]
        lines.append(f"## {split.upper()} (n={m['n_samples']})\n\n")
        lines.append(
            "| accuracy | precision (macro) | recall (macro) | F1 (macro) | F1 (weighted) |\n"
            "|----------|-------------------|----------------|------------|---------------|\n"
            f"| {m['accuracy']:.4f} | {m['precision_macro']:.4f} | {m['recall_macro']:.4f} | "
            f"{m['f1_macro']:.4f} | {m['f1_weighted']:.4f} |\n\n"
        )
        lines.append("| clase | precision | recall | F1 | support |\n|-------|-----------|--------|-----|--------|\n")
        for label in m["labels"]:
            pc = m["per_class"][label]
            lines.append(
                f"| {label} | {pc['precision']:.4f} | {pc['recall']:.4f} | "
                f"{pc['f1']:.4f} | {pc['support']} |\n"
            )
        lines.append("\n")
    path.write_text("".join(lines), encoding="utf-8")


def main() -> None:
    os.environ.setdefault("EVAL_BATCH_SIZE", "4")
    os.environ.setdefault("TRAIN_BATCH_SIZE", "4")
    _configure_tf()
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    model, source = _load_model()
    print(f"Modelo: {source}", flush=True)

    all_metrics = _evaluate_all_splits(model)
    for split, m in all_metrics.items():
        _plot_confusion_matrix(
            np.array(m["confusion_matrix"]),
            REPORTS_DIR / f"confusion_matrix_{split}.png",
            f"Matriz — {split}",
        )

    report = {
        "model_version": "rx_resnet50_v1",
        "source": source,
        "evaluated_at": datetime.now(timezone.utc).isoformat(),
        "metrics_by_split": all_metrics,
        "summary": {
            split: {
                "accuracy": all_metrics[split]["accuracy"],
                "precision_macro": all_metrics[split]["precision_macro"],
                "recall_macro": all_metrics[split]["recall_macro"],
                "f1_macro": all_metrics[split]["f1_macro"],
                "f1_weighted": all_metrics[split]["f1_weighted"],
            }
            for split in ("train", "validation", "test")
        },
    }
    (REPORTS_DIR / "training_report_v1.json").write_text(
        json.dumps(report, indent=2), encoding="utf-8"
    )
    _write_markdown(all_metrics, REPORTS_DIR / "metrics_summary.md")

    print("\n=== RESUMEN TEST ===", flush=True)
    t = all_metrics["test"]
    for k in ("accuracy", "precision_macro", "recall_macro", "f1_macro", "f1_weighted"):
        print(f"  {k}: {t[k]:.4f}", flush=True)
    print(f"Informe: {REPORTS_DIR / 'training_report_v1.json'}", flush=True)


if __name__ == "__main__":
    main()
