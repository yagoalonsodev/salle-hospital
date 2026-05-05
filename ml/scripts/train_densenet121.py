#!/usr/bin/env python3
"""Entrenamiento DenseNet121 — comparativa de arquitecturas."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from models.architectures import build_transfer_classifier  # noqa: E402
from training_core import ModelSpec, run_training  # noqa: E402

SPEC = ModelSpec(
    arch_id="densenet121",
    model_version="rx_densenet121_v1",
    build_model=lambda: build_transfer_classifier("densenet121", trainable_backbone=False),
    finetune=True,
    finetune_layers=int(__import__("os").environ.get("FINETUNE_LAYERS", "40")),
)


def main() -> None:
    run_training(SPEC)


if __name__ == "__main__":
    main()
