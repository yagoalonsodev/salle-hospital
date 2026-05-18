#!/usr/bin/env python3
"""Reinicia salle-ml para cargar el modelo .h5 recién entrenado."""

from __future__ import annotations

import os
import sys
import time

try:
    import docker
except ImportError:
    print("ERROR: pip install docker", file=sys.stderr)
    sys.exit(1)

ML_CONTAINER = os.environ.get("ML_CONTAINER", "salle-ml")
WAIT_SEC = int(os.environ.get("ML_RELOAD_WAIT_SEC", "90"))


def main() -> int:
    client = docker.from_env()
    try:
        container = client.containers.get(ML_CONTAINER)
    except docker.errors.NotFound:
        print(f"Contenedor no encontrado: {ML_CONTAINER}", file=sys.stderr)
        return 1

    print(f"Reiniciando {ML_CONTAINER}…")
    container.restart(timeout=120)
    deadline = time.time() + WAIT_SEC
    while time.time() < deadline:
        container.reload()
        health = (container.attrs.get("State") or {}).get("Health") or {}
        status = health.get("Status")
        if status == "healthy":
            print(f"{ML_CONTAINER} healthy tras reinicio.")
            return 0
        if container.status == "running" and not health:
            print(f"{ML_CONTAINER} en ejecución (sin healthcheck).")
            return 0
        time.sleep(5)
    print(f"WARN: {ML_CONTAINER} no healthy en {WAIT_SEC}s; revisar logs.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
