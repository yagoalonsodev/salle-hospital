"""Lógica compartida de entrenamiento RX — usada por train_*.py."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

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

def _features_root() -> Path:
    return Path(
        os.environ.get("FEATURES_ROOT", ROOT.parent / "data" / "processed" / "features")
    )


def _features_version() -> str:
    return os.environ.get("FEATURES_VERSION", "v1")


def get_data_dir() -> Path:
    """Ruta del dataset; lee FEATURES_ROOT en cada llamada (notebook vs Docker)."""
    return _features_root() / _features_version()


def refresh_paths() -> Path:
    """Actualiza FEATURES_ROOT / DATA_DIR tras cambiar os.environ (notebook)."""
    global FEATURES_ROOT, FEATURES_VERSION, DATA_DIR
    FEATURES_ROOT = _features_root()
    FEATURES_VERSION = _features_version()
    DATA_DIR = get_data_dir()
    return DATA_DIR


FEATURES_ROOT = _features_root()
FEATURES_VERSION = _features_version()
DATA_DIR = get_data_dir()
MODELS_DIR = ROOT / "models"
CHECKPOINT_DIR = MODELS_DIR / "checkpoints"
REPORTS_DIR = MODELS_DIR / "reports"

BATCH_SIZE = int(os.environ.get("TRAIN_BATCH_SIZE", "8"))
EVAL_BATCH_SIZE = int(os.environ.get("EVAL_BATCH_SIZE", "8"))
HEAD_EPOCHS = int(os.environ.get("HEAD_EPOCHS", os.environ.get("COMPARE_HEAD_EPOCHS", "10")))
FINETUNE_EPOCHS = int(
    os.environ.get("FINETUNE_EPOCHS", os.environ.get("COMPARE_FINETUNE_EPOCHS", "8"))
)
SEED = int(os.environ.get("RANDOM_SEED", "42"))
EXPORT_SAVEDMODEL = os.environ.get("EXPORT_SAVEDMODEL", "1") == "1"

from models.architectures import LABELS  # noqa: E402


@dataclass(frozen=True)
class ModelSpec:
    arch_id: str
    model_version: str
    build_model: Callable[[], keras.Model]
    finetune: bool = True
    finetune_layers: int = 40
    head_lr: float = 1e-3
    finetune_lr: float = 1e-5
    legacy_reports: bool = False

    @property
    def report_dir(self) -> Path:
        if self.legacy_reports:
            return REPORTS_DIR
        return REPORTS_DIR / self.model_version

    @property
    def h5_path(self) -> Path:
        return MODELS_DIR / f"{self.model_version}.h5"

    @property
    def savedmodel_dir(self) -> Path:
        return MODELS_DIR / "savedmodel" / self.model_version

    @property
    def checkpoint_pattern(self) -> str:
        return str(CHECKPOINT_DIR / f"{self.model_version}_{{epoch:02d}}_val{{val_accuracy:.4f}}.keras")

    @property
    def report_json(self) -> Path:
        name = "training_report_v1.json" if self.legacy_reports else "training_report.json"
        return self.report_dir / name


def _configure_tf() -> None:
    try:
        for device in tf.config.list_physical_devices("GPU"):
            tf.config.experimental.set_memory_growth(device, True)
    except Exception:
        pass
    tf.config.threading.set_intra_op_parallelism_threads(
        int(os.environ.get("TF_INTRA_THREADS", "4"))
    )
    tf.config.threading.set_inter_op_parallelism_threads(
        int(os.environ.get("TF_INTER_THREADS", "2"))
    )


def _dataset(split: str, shuffle: bool, batch_size: int | None = None) -> tf.data.Dataset:
    bs = batch_size or BATCH_SIZE
    ds = keras.utils.image_dataset_from_directory(
        get_data_dir() / split,
        labels="inferred",
        label_mode="int",
        class_names=list(LABELS),
        color_mode="rgb",
        batch_size=bs,
        image_size=(224, 224),
        shuffle=shuffle,
        seed=SEED,
    )
    if batch_size is not None:
        return ds
    return ds.prefetch(tf.data.AUTOTUNE)


def _class_weights() -> dict[int, float]:
    train_dir = get_data_dir() / "train"
    counts = [len(list((train_dir / label).glob("*.jpg"))) for label in LABELS]
    total = sum(counts)
    n = len(LABELS)
    return {i: total / (n * c) for i, c in enumerate(counts)}


def _merge_histories(a: keras.callbacks.History, b: keras.callbacks.History | None) -> dict:
    if b is None:
        merged = {k: list(v) for k, v in a.history.items()}
        merged["phase_boundary_epoch"] = None
        return merged
    keys = set(a.history) | set(b.history)
    merged = {k: list(a.history.get(k, [])) + list(b.history.get(k, [])) for k in keys}
    merged["phase_boundary_epoch"] = len(a.history.get("loss", []))
    return merged


def _plot_curves(history: dict, path: Path) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(12, 4))
    epochs = range(1, len(history["loss"]) + 1)
    boundary = history.get("phase_boundary_epoch")
    for ax, key, title in (
        (axes[0], "loss", "Loss"),
        (axes[1], "accuracy", "Accuracy"),
    ):
        ax.plot(epochs, history[key], label="train")
        val_key = f"val_{key}"
        if val_key in history:
            ax.plot(epochs, history[val_key], label="val")
        if boundary:
            ax.axvline(boundary, color="gray", linestyle="--", label="fine-tune")
        ax.set_title(title)
        ax.legend()
        ax.set_xlabel("Época")
    fig.tight_layout()
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=120)
    plt.close(fig)


def _plot_confusion_matrix(cm: np.ndarray, path: Path, title: str) -> None:
    fig, ax = plt.subplots(figsize=(6, 5))
    im = ax.imshow(cm, cmap="Blues")
    ax.set_xticks(range(len(LABELS)), LABELS, rotation=45)
    ax.set_yticks(range(len(LABELS)), LABELS)
    ax.set_xlabel("Predicción")
    ax.set_ylabel("Real")
    ax.set_title(title)
    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]):
            ax.text(j, i, int(cm[i, j]), ha="center", va="center", color="black")
    fig.colorbar(im, ax=ax)
    fig.tight_layout()
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=120)
    plt.close(fig)


def _evaluate_split(model: keras.Model, split: str) -> dict:
    ds = _dataset(split, shuffle=False, batch_size=EVAL_BATCH_SIZE)
    y_true, y_pred = [], []
    for batch_x, batch_y in ds:
        probs = model.predict(batch_x, verbose=0)
        y_pred.extend(np.argmax(probs, axis=1).tolist())
        y_true.extend(batch_y.numpy().tolist())

    report = classification_report(
        y_true, y_pred, target_names=list(LABELS), output_dict=True, zero_division=0
    )
    cm = confusion_matrix(y_true, y_pred)
    return {
        "split": split,
        "n_samples": len(y_true),
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "precision_macro": float(
            precision_score(y_true, y_pred, average="macro", zero_division=0)
        ),
        "recall_macro": float(recall_score(y_true, y_pred, average="macro", zero_division=0)),
        "f1_macro": float(f1_score(y_true, y_pred, average="macro", zero_division=0)),
        "precision_weighted": float(
            precision_score(y_true, y_pred, average="weighted", zero_division=0)
        ),
        "recall_weighted": float(
            recall_score(y_true, y_pred, average="weighted", zero_division=0)
        ),
        "f1_weighted": float(
            f1_score(y_true, y_pred, average="weighted", zero_division=0)
        ),
        "per_class": {
            label: {
                "precision": report[label]["precision"],
                "recall": report[label]["recall"],
                "f1": report[label]["f1-score"],
                "support": int(report[label]["support"]),
            }
            for label in LABELS
        },
        "classification_report": report,
        "confusion_matrix": cm.tolist(),
        "labels": list(LABELS),
    }


def evaluate_all_splits(model: keras.Model) -> dict[str, dict]:
    return {split: _evaluate_split(model, split) for split in ("train", "validation", "test")}


_evaluate_all_splits = evaluate_all_splits


def fn_neumonia_sana(cm: list[list[int]]) -> int:
    return int(cm[1][2])


def _set_finetune_layers(model: keras.Model, n_layers: int) -> None:
    backbone = model.layers[2]
    backbone.trainable = True
    for layer in backbone.layers[:-n_layers]:
        layer.trainable = False


def run_training(spec: ModelSpec, skip_if_report: bool = False) -> dict:
    if skip_if_report and spec.report_json.is_file():
        print(f"[{spec.arch_id}] Informe existente: {spec.report_json}", flush=True)
        return json.loads(spec.report_json.read_text(encoding="utf-8"))

    data_dir = refresh_paths()
    if not (data_dir / "train").is_dir():
        raise SystemExit(
            f"No existe dataset en {data_dir}. "
            f"FEATURES_ROOT={os.environ.get('FEATURES_ROOT')!r} — ejecuta preprocess_images (Día 3)."
        )

    _configure_tf()
    for d in (CHECKPOINT_DIR, spec.report_dir, spec.savedmodel_dir.parent):
        d.mkdir(parents=True, exist_ok=True)

    tf.keras.utils.set_random_seed(SEED)
    train_ds = _dataset("train", shuffle=True)
    val_ds = _dataset("validation", shuffle=False)
    class_weights = _class_weights()
    print(f"=== {spec.arch_id} ({spec.model_version}) ===", flush=True)
    print("Class weights:", class_weights, flush=True)

    model = spec.build_model()
    params = model.count_params()
    print(f"Parámetros totales: {params:,}", flush=True)

    log_p1 = spec.report_dir / "training_log_phase1.csv"
    log_p2 = spec.report_dir / "training_log_phase2.csv"
    curves_path = spec.report_dir / "training_curves.png"

    callbacks_p1 = [
        keras.callbacks.ModelCheckpoint(
            filepath=spec.checkpoint_pattern,
            monitor="val_accuracy",
            save_best_only=True,
            mode="max",
        ),
        keras.callbacks.EarlyStopping(
            monitor="val_loss", patience=4, restore_best_weights=True
        ),
        keras.callbacks.CSVLogger(str(log_p1)),
    ]

    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=spec.head_lr),
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"],
    )

    head_epochs = HEAD_EPOCHS
    print(
        "=== Fase 1: cabeza (backbone congelado) ==="
        if spec.finetune
        else "=== Entrenamiento completo (baseline) ===",
        flush=True,
    )
    hist1 = model.fit(
        train_ds,
        validation_data=val_ds,
        epochs=head_epochs,
        class_weight=class_weights,
        callbacks=callbacks_p1,
        verbose=1,
    )

    hist2 = None
    if spec.finetune:
        _set_finetune_layers(model, spec.finetune_layers)
        trainable = sum(int(tf.size(w)) for w in model.trainable_weights)
        print(f"Parámetros entrenables (fine-tune): {trainable:,}", flush=True)
        model.compile(
            optimizer=keras.optimizers.Adam(learning_rate=spec.finetune_lr),
            loss="sparse_categorical_crossentropy",
            metrics=["accuracy"],
        )
        callbacks_p2 = [
            keras.callbacks.ModelCheckpoint(
                filepath=spec.checkpoint_pattern,
                monitor="val_accuracy",
                save_best_only=True,
                mode="max",
            ),
            keras.callbacks.EarlyStopping(
                monitor="val_loss", patience=4, restore_best_weights=True
            ),
            keras.callbacks.CSVLogger(str(log_p2)),
        ]
        print("=== Fase 2: fine-tuning ===", flush=True)
        hist2 = model.fit(
            train_ds,
            validation_data=val_ds,
            epochs=FINETUNE_EPOCHS,
            class_weight=class_weights,
            callbacks=callbacks_p2,
            verbose=1,
        )

    history = _merge_histories(hist1, hist2)
    _plot_curves(history, curves_path)

    print("=== Evaluación train / validation / test ===", flush=True)
    all_metrics = evaluate_all_splits(model)
    for split, m in all_metrics.items():
        _plot_confusion_matrix(
            np.array(m["confusion_matrix"]),
            spec.report_dir / f"confusion_matrix_{split}.png",
            title=f"{spec.model_version} — {split}",
        )

    model.save(spec.h5_path)
    if EXPORT_SAVEDMODEL:
        import shutil

        try:
            if spec.savedmodel_dir.exists():
                shutil.rmtree(spec.savedmodel_dir)
            model.export(spec.savedmodel_dir)
        except Exception as exc:
            print(f"⚠ SavedModel no exportado: {exc}", flush=True)

    test_m = all_metrics["test"]
    report = {
        "arch_id": spec.arch_id,
        "model_version": spec.model_version,
        "features_dir": str(data_dir),
        "trained_at": datetime.now(timezone.utc).isoformat(),
        "hyperparameters": {
            "batch_size": BATCH_SIZE,
            "head_epochs": head_epochs,
            "finetune_epochs": FINETUNE_EPOCHS if spec.finetune else 0,
            "finetune_layers": spec.finetune_layers if spec.finetune else 0,
            "finetune": spec.finetune,
            "seed": SEED,
            "class_weights": class_weights,
            "total_params": params,
        },
        "history": {
            k: [float(x) if x is not None else None for x in v]
            for k, v in history.items()
            if k != "phase_boundary_epoch"
        },
        "phase_boundary_epoch": history.get("phase_boundary_epoch"),
        "metrics_by_split": all_metrics,
        "fn_neumonia_sana": fn_neumonia_sana(test_m["confusion_matrix"]),
        "summary": {
            "test": {
                "accuracy": test_m["accuracy"],
                "precision_macro": test_m["precision_macro"],
                "recall_macro": test_m["recall_macro"],
                "f1_macro": test_m["f1_macro"],
                "f1_weighted": test_m["f1_weighted"],
            }
        },
        "artifacts": {
            "h5": str(spec.h5_path.relative_to(ROOT)),
            "report": str(spec.report_json.relative_to(ROOT)),
        },
    }
    spec.report_json.write_text(json.dumps(report, indent=2), encoding="utf-8")

    md_lines = [f"# Métricas {spec.model_version}\n", f"Entrenado: {report['trained_at']}\n"]
    for split in ("train", "validation", "test"):
        m = all_metrics[split]
        md_lines.append(f"\n## {split.upper()} (n={m['n_samples']})\n")
        md_lines.append(
            "| accuracy | precision (macro) | recall (macro) | F1 (macro) | F1 (weighted) |\n"
            "|----------|-------------------|----------------|------------|---------------|\n"
        )
        md_lines.append(
            f"| {m['accuracy']:.4f} | {m['precision_macro']:.4f} | "
            f"{m['recall_macro']:.4f} | {m['f1_macro']:.4f} | {m['f1_weighted']:.4f} |\n"
        )
    (spec.report_dir / "metrics_summary.md").write_text("".join(md_lines), encoding="utf-8")

    print("\n=== TEST ===", flush=True)
    print(f"accuracy: {test_m['accuracy']:.4f}", flush=True)
    print(f"f1_macro: {test_m['f1_macro']:.4f}", flush=True)
    print(f"FN neumonía→sana: {report['fn_neumonia_sana']}", flush=True)
    print(f"Informe: {spec.report_json}", flush=True)
    return report


def load_report(spec: ModelSpec) -> dict:
    if not spec.report_json.is_file():
        raise FileNotFoundError(spec.report_json)
    return json.loads(spec.report_json.read_text(encoding="utf-8"))


def report_to_comparison_entry(report: dict) -> dict:
    test = report["metrics_by_split"]["test"]
    hp = report.get("hyperparameters", {})
    return {
        "model_version": report["model_version"],
        "test": report["summary"]["test"],
        "fn_neumonia_sana": report.get(
            "fn_neumonia_sana", fn_neumonia_sana(test["confusion_matrix"])
        ),
        "epochs": {
            "head": hp.get("head_epochs", HEAD_EPOCHS),
            "finetune": hp.get("finetune_epochs", 0),
        },
        "total_params": hp.get("total_params"),
        "report_path": report.get("artifacts", {}).get("report"),
    }


def build_architecture_comparison(reports: dict[str, dict]) -> dict:
    ranking = sorted(
        reports.keys(),
        key=lambda a: (
            -reports[a]["test"]["f1_macro"],
            reports[a]["fn_neumonia_sana"],
            -reports[a]["test"]["accuracy"],
        ),
    )
    recommended = ranking[0] if ranking else None
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "models": reports,
        "ranking_test_f1_macro": ranking,
        "recommended": recommended,
        "production_model": "resnet50",
    }


def write_architecture_comparison(reports: dict[str, dict]) -> Path:
    payload = build_architecture_comparison(reports)
    out = REPORTS_DIR / "architecture_comparison.json"
    out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return out
