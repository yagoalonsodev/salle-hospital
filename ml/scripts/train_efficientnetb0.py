#!/usr/bin/env python3
"""Entrenamiento EfficientNetB0 — comparativa de arquitecturas."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from models.architectures import build_transfer_classifier  # noqa: E402
from training_core import ModelSpec, run_training  # noqa: E402

SPEC = ModelSpec(
    arch_id="efficientnetb0",
    model_version="rx_efficientnetb0_v1",
    build_model=lambda: build_transfer_classifier("efficientnetb0", trainable_backbone=False),
    finetune=True,
    finetune_layers=int(__import__("os").environ.get("FINETUNE_LAYERS", "30")),
)


def main() -> None:
    run_training(SPEC)


if __name__ == "__main__":
    main()
