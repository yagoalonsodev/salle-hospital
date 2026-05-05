#!/usr/bin/env python3
"""Evalúa un checkpoint, exporta .h5 / SavedModel y genera informes (Día 5)."""

from __future__ import annotations

import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import tensorflow as tf
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)
from tensorflow import keras

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from models.architectures import LABELS  # noqa: E402

FEATURES_ROOT = Path(
    os.environ.get("FEATURES_ROOT", ROOT.parent / "data" / "processed" / "features")
)
FEATURES_VERSION = os.environ.get("FEATURES_VERSION", "v1")
DATA_DIR = FEATURES_ROOT / FEATURES_VERSION
MODELS_DIR = ROOT / "models"
CHECKPOINT_DIR = MODELS_DIR / "checkpoints"
REPORTS_DIR = MODELS_DIR / "reports"
SAVEDMODEL_DIR = MODELS_DIR / "savedmodel" / "rx_resnet50_v1"
BATCH_SIZE = int(os.environ.get("TRAIN_BATCH_SIZE", "32"))
SEED = int(os.environ.get("RANDOM_SEED", "42"))


def _best_checkpoint() -> Path:
    pattern = re.compile(r"val([0-9.]+)\.keras$")
    best_path: Path | None = None
    best_val = -1.0
    for path in CHECKPOINT_DIR.glob("rx_resnet50_v1_*.keras"):
        match = pattern.search(path.name)
        if not match:
            continue
        val = float(match.group(1))
        if val > best_val:
            best_val = val
            best_path = path
    if best_path is None:
        raise FileNotFoundError(f"No hay checkpoints en {CHECKPOINT_DIR}")
    return best_path


def _test_dataset() -> tf.data.Dataset:
    return keras.utils.image_dataset_from_directory(
        DATA_DIR / "test",
        labels="inferred",
        label_mode="int",
        class_names=list(LABELS),
        color_mode="rgb",
        batch_size=BATCH_SIZE,
        image_size=(224, 224),
        shuffle=False,
        seed=SEED,
    ).prefetch(tf.data.AUTOTUNE)


def _evaluate(model: keras.Model, test_ds: tf.data.Dataset) -> dict:
    y_true, y_pred = [], []
    for batch_x, batch_y in test_ds:
        probs = model.predict(batch_x, verbose=0)
        y_pred.extend(np.argmax(probs, axis=1).tolist())
        y_true.extend(batch_y.numpy().tolist())
    report = classification_report(
        y_true, y_pred, target_names=list(LABELS), output_dict=True, zero_division=0
    )
    cm = confusion_matrix(y_true, y_pred)
    return {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "precision_macro": float(precision_score(y_true, y_pred, average="macro", zero_division=0)),
        "recall_macro": float(recall_score(y_true, y_pred, average="macro", zero_division=0)),
        "f1_macro": float(f1_score(y_true, y_pred, average="macro", zero_division=0)),
        "classification_report": report,
        "confusion_matrix": cm.tolist(),
        "labels": list(LABELS),
    }


def _plot_confusion_matrix(cm: np.ndarray, path: Path) -> None:
    fig, ax = plt.subplots(figsize=(6, 5))
    im = ax.imshow(cm, cmap="Blues")
    ax.set_xticks(range(len(LABELS)), LABELS, rotation=45)
    ax.set_yticks(range(len(LABELS)), LABELS)
    ax.set_xlabel("Predicción")
    ax.set_ylabel("Real")
    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]):
            ax.text(j, i, int(cm[i, j]), ha="center", va="center", color="black")
    fig.colorbar(im, ax=ax)
    fig.tight_layout()
    fig.savefig(path, dpi=120)
    plt.close(fig)


def _plot_curves_from_csv(csv_path: Path, out_path: Path) -> None:
    if not csv_path.is_file():
        return
    import pandas as pd

    df = pd.read_csv(csv_path)
    fig, axes = plt.subplots(1, 2, figsize=(12, 4))
    axes[0].plot(df["loss"], label="train")
    if "val_loss" in df.columns:
        axes[0].plot(df["val_loss"], label="val")
    axes[0].set_title("Loss")
    axes[0].legend()
    axes[1].plot(df["accuracy"], label="train")
    if "val_accuracy" in df.columns:
        axes[1].plot(df["val_accuracy"], label="val")
    axes[1].set_title("Accuracy")
    axes[1].legend()
    fig.tight_layout()
    fig.savefig(out_path, dpi=120)
    plt.close(fig)


def main() -> None:
    checkpoint = _best_checkpoint()
    print(f"Checkpoint: {checkpoint.name}")
    model = keras.models.load_model(checkpoint)
    test_ds = _test_dataset()
    metrics = _evaluate(model, test_ds)
    cm = np.array(metrics["confusion_matrix"])
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    _plot_confusion_matrix(cm, REPORTS_DIR / "confusion_matrix_test.png")
    _plot_curves_from_csv(REPORTS_DIR / "training_log.csv", REPORTS_DIR / "training_curves.png")

    h5_path = MODELS_DIR / "rx_resnet50_v1.h5"
    model.save(h5_path)
    if SAVEDMODEL_DIR.exists():
        import shutil

        shutil.rmtree(SAVEDMODEL_DIR)
    model.export(SAVEDMODEL_DIR)

    report = {
        "model_version": "rx_resnet50_v1",
        "checkpoint_source": checkpoint.name,
        "features_dir": str(DATA_DIR),
        "finalized_at": datetime.now(timezone.utc).isoformat(),
        "test_metrics": metrics,
        "artifacts": {
            "h5": str(h5_path.name),
            "savedmodel": "savedmodel/rx_resnet50_v1",
            "confusion_matrix": "reports/confusion_matrix_test.png",
            "training_curves": "reports/training_curves.png",
        },
    }
    (REPORTS_DIR / "training_report_v1.json").write_text(
        json.dumps(report, indent=2), encoding="utf-8"
    )
    print(json.dumps({k: metrics[k] for k in ("accuracy", "precision_macro", "recall_macro", "f1_macro")}, indent=2))


if __name__ == "__main__":
    main()
