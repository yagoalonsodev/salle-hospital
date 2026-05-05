#!/usr/bin/env python3
"""Entrenamiento baseline CNN — comparativa de arquitecturas."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from models.architectures import build_baseline_cnn  # noqa: E402
from training_core import ModelSpec, run_training  # noqa: E402

SPEC = ModelSpec(
    arch_id="baseline_cnn",
    model_version="rx_baseline_cnn_v1",
    build_model=build_baseline_cnn,
    finetune=False,
)


def main() -> None:
    run_training(SPEC)


if __name__ == "__main__":
    main()
