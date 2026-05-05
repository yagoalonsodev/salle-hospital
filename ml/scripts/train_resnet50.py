#!/usr/bin/env python3
"""Entrenamiento ResNet50 — clasificación RX (modelo de producción v1)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from models.architectures import build_transfer_classifier  # noqa: E402
from training_core import (  # noqa: E402
    BATCH_SIZE,
    CHECKPOINT_DIR,
    DATA_DIR,
    EVAL_BATCH_SIZE,
    FEATURES_ROOT,
    FEATURES_VERSION,
    FINETUNE_EPOCHS,
    HEAD_EPOCHS,
    MODELS_DIR,
    REPORTS_DIR,
    SEED,
    ModelSpec,
    _class_weights,
    _configure_tf,
    _dataset,
    _evaluate_all_splits,
    _merge_histories,
    _plot_confusion_matrix,
    _plot_curves,
    run_training,
)

# Re-export para export_all_metrics.py y finetune_from_checkpoint.py
__all__ = [
    "BATCH_SIZE",
    "CHECKPOINT_DIR",
    "DATA_DIR",
    "EVAL_BATCH_SIZE",
    "FEATURES_ROOT",
    "FEATURES_VERSION",
    "FINETUNE_EPOCHS",
    "HEAD_EPOCHS",
    "MODELS_DIR",
    "REPORTS_DIR",
    "SEED",
    "_class_weights",
    "_configure_tf",
    "_dataset",
    "_evaluate_all_splits",
    "_merge_histories",
    "_plot_confusion_matrix",
    "_plot_curves",
    "evaluate_all_splits",
]

SAVEDMODEL_DIR = MODELS_DIR / "savedmodel" / "rx_resnet50_v1"

SPEC = ModelSpec(
    arch_id="resnet50",
    model_version="rx_resnet50_v1",
    build_model=lambda: build_transfer_classifier("resnet50", trainable_backbone=False),
    finetune=True,
    finetune_layers=int(__import__("os").environ.get("FINETUNE_LAYERS", "40")),
    legacy_reports=True,
)


def main() -> None:
    run_training(SPEC)


if __name__ == "__main__":
    main()
