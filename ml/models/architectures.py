"""Arquitecturas Keras para clasificación RX — salle-hospital."""

from __future__ import annotations

from typing import Literal

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import applications, layers

NUM_CLASSES = 3
LABELS = ("covid", "neumonia", "sana")
DEFAULT_IMAGE_SIZE = 224

BackboneName = Literal["resnet50", "efficientnetb0", "densenet121"]


def build_baseline_cnn(
    image_size: int = DEFAULT_IMAGE_SIZE,
    num_classes: int = NUM_CLASSES,
) -> keras.Model:
    """CNN pequeña desde cero — baseline para comparar con Transfer Learning."""
    inputs = keras.Input(shape=(image_size, image_size, 3), name="rx_image")
    x = layers.Rescaling(1.0 / 255, name="rescaling")(inputs)
    for i, filters in enumerate((32, 64, 128), start=1):
        x = layers.Conv2D(filters, 3, padding="same", activation="relu", name=f"conv_{i}")(x)
        x = layers.MaxPooling2D(name=f"pool_{i}")(x)
    x = layers.GlobalAveragePooling2D(name="gap")(x)
    x = layers.Dropout(0.3, name="dropout")(x)
    outputs = layers.Dense(num_classes, activation="softmax", name="predictions")(x)
    return keras.Model(inputs, outputs, name="baseline_cnn")


def _load_backbone(
    backbone: BackboneName,
    image_size: int,
    weights: str | None,
) -> keras.Model:
    kwargs: dict = {
        "include_top": False,
        "weights": weights,
        "input_shape": (image_size, image_size, 3),
    }
    if backbone == "resnet50":
        return applications.ResNet50(**kwargs)
    if backbone == "efficientnetb0":
        return applications.EfficientNetB0(**kwargs)
    if backbone == "densenet121":
        return applications.DenseNet121(**kwargs)
    raise ValueError(f"backbone no soportado: {backbone}")


def build_transfer_classifier(
    backbone: BackboneName = "resnet50",
    image_size: int = DEFAULT_IMAGE_SIZE,
    num_classes: int = NUM_CLASSES,
    trainable_backbone: bool = False,
    weights: str | None = "imagenet",
    dropout: float = 0.4,
) -> keras.Model:
    """Transfer Learning: backbone ImageNet + cabeza densa multiclase."""
    base = _load_backbone(backbone, image_size, weights)
    base.trainable = trainable_backbone

    inputs = keras.Input(shape=(image_size, image_size, 3), name="rx_image")
    x = layers.Rescaling(1.0 / 255, name="rescaling")(inputs)
    x = base(x, training=False)
    x = layers.GlobalAveragePooling2D(name="gap")(x)
    x = layers.Dropout(dropout, name="dropout")(x)
    outputs = layers.Dense(num_classes, activation="softmax", name="predictions")(x)
    return keras.Model(inputs, outputs, name=f"{backbone}_rx_classifier")


def count_parameters(model: keras.Model) -> dict[str, int]:
    trainable = int(
        sum(tf.keras.backend.count_params(w) for w in model.trainable_weights)
    )
    total = int(model.count_params())
    return {
        "trainable": trainable,
        "non_trainable": total - trainable,
        "total": total,
    }


def compare_architectures(image_size: int = DEFAULT_IMAGE_SIZE) -> list[dict[str, object]]:
    """Tabla de comparación para notebook / informes (backbone congelado)."""
    specs: list[tuple[str, keras.Model]] = [
        ("baseline_cnn", build_baseline_cnn(image_size)),
        ("resnet50", build_transfer_classifier("resnet50", image_size, trainable_backbone=False)),
        (
            "efficientnetb0",
            build_transfer_classifier("efficientnetb0", image_size, trainable_backbone=False),
        ),
        (
            "densenet121",
            build_transfer_classifier("densenet121", image_size, trainable_backbone=False),
        ),
    ]
    rows: list[dict[str, object]] = []
    for name, model in specs:
        params = count_parameters(model)
        rows.append({"architecture": name, **params})
    return rows
