"""Cliente HTTP al servicio ML."""

from __future__ import annotations

import io
from typing import Any

import httpx

from app.config import ml_service_url


def check_ml() -> tuple[bool, str | None, dict[str, Any] | None]:
    try:
        r = httpx.get(f"{ml_service_url()}/health", timeout=5.0)
        data = r.json() if r.headers.get("content-type", "").startswith("application/json") else {}
        ok = r.status_code == 200 and data.get("model_loaded") is True
        return ok, None if ok else data.get("load_error") or r.text, data
    except Exception as exc:  # noqa: BLE001
        return False, str(exc), None


def predict_bytes(raw: bytes, filename: str, content_type: str) -> dict[str, Any]:
    with httpx.Client(timeout=120.0) as client:
        files = {"file": (filename, io.BytesIO(raw), content_type)}
        r = client.post(f"{ml_service_url()}/predict", files=files)
        r.raise_for_status()
        return r.json()
