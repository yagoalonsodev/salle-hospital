#!/usr/bin/env python3
"""Fine-tuning desde el mejor checkpoint + exportación completa de métricas."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import tensorflow as tf
from tensorflow import keras

from train_resnet50 import (  # noqa: E402
    CHECKPOINT_DIR,
    FINETUNE_EPOCHS,
    FINETUNE_LAYERS,
    REPORTS_DIR,
    _class_weights,
    _configure_tf,
    _dataset,
    _evaluate_all_splits,
    _merge_histories,
    _plot_confusion_matrix,
    _plot_curves,
)
import json
import numpy as np
from datetime import datetime, timezone


def _best_checkpoint() -> Path:
    pattern = re.compile(r"val([0-9.]+)\.keras$")
    best_path, best_val = None, -1.0
    for path in CHECKPOINT_DIR.glob("rx_resnet50_v1_*.keras"):
        m = pattern.search(path.name)
        if m and float(m.group(1)) > best_val:
            best_val = float(m.group(1))
            best_path = path
    if best_path is None:
        raise FileNotFoundError("No hay checkpoints")
    return best_path


def main() -> None:
    _configure_tf()
    ckpt = _best_checkpoint()
    print(f"Checkpoint: {ckpt.name}", flush=True)

    model = keras.models.load_model(ckpt)
    backbone = model.layers[2]
    backbone.trainable = True
    for layer in backbone.layers[:-FINETUNE_LAYERS]:
        layer.trainable = False

    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=1e-5),
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"],
    )

    train_ds = _dataset("train", shuffle=True)
    val_ds = _dataset("validation", shuffle=False)
    class_weights = _class_weights()

    log_path = REPORTS_DIR / "training_log_phase2.csv"
    callbacks = [
        keras.callbacks.ModelCheckpoint(
            filepath=str(CHECKPOINT_DIR / "rx_resnet50_v1_{epoch:02d}_val{val_accuracy:.4f}.keras"),
            monitor="val_accuracy",
            save_best_only=True,
            mode="max",
        ),
        keras.callbacks.EarlyStopping(
            monitor="val_loss", patience=4, restore_best_weights=True
        ),
        keras.callbacks.CSVLogger(str(log_path)),
    ]

    print("=== Fine-tuning ===", flush=True)
    hist = model.fit(
        train_ds,
        validation_data=val_ds,
        epochs=FINETUNE_EPOCHS,
        class_weight=class_weights,
        callbacks=callbacks,
        verbose=1,
    )

    # Curvas: fusionar phase1 csv si existe
    import pandas as pd

    history: dict = {k: list(v) for k, v in hist.history.items()}
    p1 = REPORTS_DIR / "training_log_phase1.csv"
    if p1.is_file():
        df1 = pd.read_csv(p1)
        for col in df1.columns:
            history.setdefault(col, [])
        merged = {k: list(df1[k]) + history.get(k, []) for k in df1.columns if k in history or k == "epoch"}
        # Rebuild from both CSVs
        df2 = pd.read_csv(log_path)
        full = {
            "loss": list(df1["loss"]) + list(df2["loss"]),
            "accuracy": list(df1["accuracy"]) + list(df2["accuracy"]),
            "val_loss": list(df1["val_loss"]) + list(df2["val_loss"]),
            "val_accuracy": list(df1["val_accuracy"]) + list(df2["val_accuracy"]),
        }
        full["phase_boundary_epoch"] = len(df1)
        _plot_curves(full, REPORTS_DIR / "training_curves.png")
    else:
        _plot_curves(history, REPORTS_DIR / "training_curves.png")

    print("=== Evaluación train / validation / test ===", flush=True)
    all_metrics = _evaluate_all_splits(model)
    for split, m in all_metrics.items():
        _plot_confusion_matrix(
            np.array(m["confusion_matrix"]),
            REPORTS_DIR / f"confusion_matrix_{split}.png",
            f"Matriz — {split}",
        )

    import shutil

    h5_path = ROOT / "models" / "rx_resnet50_v1.h5"
    savedmodel = ROOT / "models" / "savedmodel" / "rx_resnet50_v1"
    model.save(h5_path)
    if savedmodel.exists():
        shutil.rmtree(savedmodel)
    model.export(savedmodel)

    test_m = all_metrics["test"]
    report = {
        "model_version": "rx_resnet50_v1",
        "checkpoint_source": ckpt.name,
        "trained_at": datetime.now(timezone.utc).isoformat(),
        "finetune_epochs": FINETUNE_EPOCHS,
        "metrics_by_split": all_metrics,
        "summary": {"test": {k: test_m[k] for k in (
            "accuracy", "precision_macro", "recall_macro", "f1_macro", "f1_weighted"
        )}},
    }
    (REPORTS_DIR / "training_report_v1.json").write_text(
        json.dumps(report, indent=2), encoding="utf-8"
    )

    md = ["# Métricas rx_resnet50_v1\n\n"]
    for split in ("train", "validation", "test"):
        m = all_metrics[split]
        md.append(f"## {split.upper()} (n={m['n_samples']})\n\n")
        md.append(
            f"| accuracy | P macro | R macro | F1 macro | F1 weighted |\n"
            f"|----------|---------|---------|----------|-------------|\n"
            f"| {m['accuracy']:.4f} | {m['precision_macro']:.4f} | "
            f"{m['recall_macro']:.4f} | {m['f1_macro']:.4f} | {m['f1_weighted']:.4f} |\n\n"
        )
        md.append("| clase | precision | recall | F1 | support |\n|-------|-----------|--------|-----|--------|\n")
        for label in m["labels"]:
            pc = m["per_class"][label]
            md.append(
                f"| {label} | {pc['precision']:.4f} | {pc['recall']:.4f} | "
                f"{pc['f1']:.4f} | {pc['support']} |\n"
            )
        md.append("\n")
    (REPORTS_DIR / "metrics_summary.md").write_text("".join(md), encoding="utf-8")

    print("\n=== TEST ===", flush=True)
    for k in ("accuracy", "precision_macro", "recall_macro", "f1_macro", "f1_weighted"):
        print(f"{k}: {test_m[k]:.4f}", flush=True)


if __name__ == "__main__":
    main()
