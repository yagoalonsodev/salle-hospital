"""Carga del modelo ResNet50 y predicción sobre una imagen PIL."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import numpy as np
import tensorflow as tf
from PIL import Image

LABELS = ("covid", "neumonia", "sana")
IMAGE_SIZE = int(os.environ.get("IMAGE_SIZE", "224"))
MODEL_VERSION = os.environ.get("MODEL_VERSION", "rx_resnet50_v1")
MODEL_NAME = os.environ.get("MODEL_NAME", "resnet50")
MODEL_PATH = Path(os.environ.get("MODEL_PATH", f"models/{MODEL_VERSION}.h5"))

_model: tf.keras.Model | None = None
_load_error: str | None = None


def model_status() -> dict[str, Any]:
    return {
        "model_loaded": _model is not None,
        "model_version": MODEL_VERSION,
        "model_path": str(MODEL_PATH),
        "load_error": _load_error,
    }


def load_model() -> tf.keras.Model:
    global _model, _load_error
    if _model is not None:
        return _model
    if not MODEL_PATH.is_file():
        _load_error = f"No se encontró el modelo en {MODEL_PATH}"
        raise FileNotFoundError(_load_error)
    try:
        _model = tf.keras.models.load_model(MODEL_PATH, compile=False)
        _load_error = None
        return _model
    except Exception as exc:  # noqa: BLE001
        _load_error = str(exc)
        raise


def preprocess(image: Image.Image) -> np.ndarray:
    img = image.convert("RGB").resize(
        (IMAGE_SIZE, IMAGE_SIZE),
        Image.Resampling.BILINEAR,
    )
    return np.expand_dims(np.asarray(img, dtype=np.float32), axis=0)


def predict_pil(image: Image.Image) -> dict[str, Any]:
    model = load_model()
    probs = model.predict(preprocess(image), verbose=0)[0]
    probs = [float(p) for p in probs]
    idx = int(np.argmax(probs))
    return {
        "predicted_label": LABELS[idx],
        "probabilities": {label: probs[i] for i, label in enumerate(LABELS)},
        "confidence": probs[idx],
        "model_name": MODEL_NAME,
        "model_version": MODEL_VERSION,
    }
