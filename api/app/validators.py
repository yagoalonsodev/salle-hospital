"""Validación de radiografías subidas por la API."""

from __future__ import annotations

import io
import re
from dataclasses import dataclass

from PIL import Image, UnidentifiedImageError
from werkzeug.datastructures import FileStorage

from app.config import ALLOWED_EXTENSIONS, MAX_UPLOAD_BYTES, MIN_IMAGE_SIDE

PATIENT_ID_RE = re.compile(r"^PAT-[A-Za-z0-9]{6,12}$")

MAGIC_JPEG = (b"\xff\xd8\xff",)
MAGIC_PNG = (b"\x89PNG\r\n\x1a\n",)


@dataclass
class ValidatedImage:
    filename: str
    content_type: str
    raw: bytes
    width: int
    height: int
    pil: Image.Image


class ValidationError(Exception):
    def __init__(self, message: str, status_code: int = 400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


def _safe_filename(name: str) -> str:
    if not name or name in (".", ".."):
        raise ValidationError("Nombre de archivo no válido")
    base = name.replace("\\", "/").split("/")[-1]
    if ".." in base:
        raise ValidationError("Nombre de archivo no válido")
    return base


def _check_magic(raw: bytes) -> None:
    if raw.startswith(MAGIC_PNG):
        return
    if raw[:3] == MAGIC_JPEG[0][:3]:
        return
    raise ValidationError("Formato no reconocido (solo JPEG o PNG)")


def validate_patient_id(patient_id: str | None) -> str | None:
    if patient_id is None or patient_id.strip() == "":
        return None
    patient_id = patient_id.strip()
    if len(patient_id) > 16:
        raise ValidationError("patient_id demasiado largo")
    if not PATIENT_ID_RE.match(patient_id):
        raise ValidationError("patient_id debe tener formato PAT-xxxxxxxx")
    return patient_id


def validate_image_file(file: FileStorage | None) -> ValidatedImage:
    if file is None or not file.filename:
        raise ValidationError("Falta el archivo de imagen (campo 'file')")

    filename = _safe_filename(file.filename)
    ext = ("." + filename.rsplit(".", 1)[-1].lower()) if "." in filename else ""
    if ext not in ALLOWED_EXTENSIONS:
        raise ValidationError(
            f"Extensión no permitida. Use: {', '.join(sorted(ALLOWED_EXTENSIONS))}"
        )

    raw = file.read()
    if not raw:
        raise ValidationError("Archivo vacío")
    if len(raw) > MAX_UPLOAD_BYTES:
        raise ValidationError(
            f"Archivo demasiado grande (máx. {MAX_UPLOAD_BYTES // (1024 * 1024)} MB)",
            status_code=413,
        )

    _check_magic(raw)

    try:
        pil = Image.open(io.BytesIO(raw))
        pil.verify()
        pil = Image.open(io.BytesIO(raw)).convert("RGB")
    except (UnidentifiedImageError, OSError) as exc:
        raise ValidationError(f"No es una imagen válida: {exc}") from exc

    w, h = pil.size
    if w < MIN_IMAGE_SIDE or h < MIN_IMAGE_SIDE:
        raise ValidationError(
            f"Imagen demasiado pequeña (mín. {MIN_IMAGE_SIDE}×{MIN_IMAGE_SIDE} px)"
        )

    content_type = file.content_type or "image/jpeg"
    if not content_type.startswith("image/"):
        content_type = "image/jpeg" if ext in (".jpg", ".jpeg") else "image/png"

    return ValidatedImage(
        filename=filename,
        content_type=content_type,
        raw=raw,
        width=w,
        height=h,
        pil=pil,
    )
