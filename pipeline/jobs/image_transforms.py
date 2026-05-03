"""Transformaciones de imagen RX (PIL) — usado desde preprocess_images.py en workers Spark."""

from __future__ import annotations

import random
from io import BytesIO
from typing import Literal

from PIL import Image, ImageOps

AugmentType = Literal["original", "rotate", "flip", "zoom"]

LABEL_FROM_FOLDER = {
    "NORMAL": "sana",
    "PNEUMONIA": "neumonia",
    "COVID19": "covid",
}


def load_rgb(path: str) -> Image.Image:
    with Image.open(path) as img:
        return img.convert("RGB")


def resize(img: Image.Image, size: int) -> Image.Image:
    return ImageOps.fit(img, (size, size), method=Image.Resampling.LANCZOS)


def normalize_to_uint8(img: Image.Image) -> Image.Image:
    """Escala píxeles a [0,1] por canal y vuelve a uint8 (estabiliza contraste)."""
    import numpy as np

    arr = np.asarray(img, dtype=np.float32) / 255.0
    arr = (arr - arr.mean()) / (arr.std() + 1e-6)
    arr = (arr - arr.min()) / (arr.max() - arr.min() + 1e-6)
    arr = (arr * 255.0).clip(0, 255).astype("uint8")
    return Image.fromarray(arr, mode="RGB")


def augment_rotate(img: Image.Image, rng: random.Random, degrees: float = 15.0) -> Image.Image:
    angle = rng.uniform(-degrees, degrees)
    return img.rotate(angle, resample=Image.Resampling.BILINEAR, expand=False)


def augment_flip(img: Image.Image) -> Image.Image:
    return ImageOps.mirror(img)


def augment_zoom(img: Image.Image, rng: random.Random, scale: float = 1.1) -> Image.Image:
    w, h = img.size
    nw, nh = int(w * scale), int(h * scale)
    enlarged = img.resize((nw, nh), Image.Resampling.LANCZOS)
    left = (nw - w) // 2
    top = (nh - h) // 2
    return enlarged.crop((left, top, left + w, top + h))


def apply_augment(
    img: Image.Image, aug: AugmentType, rng: random.Random
) -> Image.Image:
    if aug == "original":
        return img
    if aug == "rotate":
        return augment_rotate(img, rng)
    if aug == "flip":
        return augment_flip(img)
    if aug == "zoom":
        return augment_zoom(img, rng)
    raise ValueError(f"augment desconocido: {aug}")


def process_and_save(
    src_path: str,
    dest_path: str,
    image_size: int,
    augment: AugmentType,
    rng: random.Random,
) -> None:
    img = load_rgb(src_path)
    img = resize(img, image_size)
    img = normalize_to_uint8(img)
    img = apply_augment(img, augment, rng)
    img = resize(img, image_size)
    dest = __import__("pathlib").Path(dest_path)
    dest.parent.mkdir(parents=True, exist_ok=True)
    buf = BytesIO()
    img.save(buf, format="JPEG", quality=95)
    dest.write_bytes(buf.getvalue())


def train_augment_types() -> list[AugmentType]:
    return ["original", "rotate", "flip", "zoom"]


def eval_augment_types() -> list[AugmentType]:
    return ["original"]
