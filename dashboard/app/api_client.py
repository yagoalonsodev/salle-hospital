"""Cliente HTTP hacia la API Flask."""

from __future__ import annotations

import os

import httpx

API_URL = os.environ.get("API_URL", "http://localhost:8000").rstrip("/")
TIMEOUT = float(os.environ.get("DASHBOARD_HTTP_TIMEOUT", "30"))


def get_dashboard() -> dict:
    r = httpx.get(f"{API_URL}/api/dashboard", timeout=TIMEOUT)
    r.raise_for_status()
    return r.json()


def get_study_image(study_id: str) -> bytes | None:
    try:
        r = httpx.get(f"{API_URL}/api/studies/{study_id}/image", timeout=TIMEOUT)
        if r.status_code == 200:
            return r.content
    except httpx.HTTPError:
        pass
    return None


def get_logs(
    collection: str = "application_logs",
    *,
    service: str | None = None,
    level: str | None = None,
    limit: int = 100,
) -> dict:
    params: dict = {"collection": collection, "limit": limit}
    if service:
        params["service"] = service
    if level:
        params["level"] = level
    r = httpx.get(f"{API_URL}/api/logs", params=params, timeout=TIMEOUT)
    r.raise_for_status()
    return r.json()


def acknowledge_alert(alert_id: int) -> bool:
    r = httpx.patch(f"{API_URL}/api/alerts/{alert_id}/ack", timeout=10.0)
    return r.status_code == 200
