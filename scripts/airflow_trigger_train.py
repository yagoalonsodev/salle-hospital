#!/usr/bin/env python3
"""Entrena ResNet50 en salle-ml (DAG reentrenamiento nocturno)."""

from __future__ import annotations

import os
import sys
from datetime import datetime, timezone
from uuid import uuid4

try:
    import docker
except ImportError:
    print("ERROR: pip install docker", file=sys.stderr)
    sys.exit(1)

ML_CONTAINER = os.environ.get("ML_CONTAINER", "salle-ml")
RUN_ID = os.environ.get(
    "PIPELINE_RUN_ID",
    f"RUN-NT-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M')}-{uuid4().hex[:6]}",
)


def main() -> int:
    client = docker.from_env()
    try:
        container = client.containers.get(ML_CONTAINER)
    except docker.errors.NotFound:
        print(f"Contenedor no encontrado: {ML_CONTAINER}", file=sys.stderr)
        return 1

    cmd = ["python", "scripts/train_resnet50.py"]
    env = {
        "FEATURES_ROOT": os.environ.get(
            "FEATURES_ROOT", "/opt/data/processed/features"
        ),
        "FEATURES_VERSION": os.environ.get("FEATURES_VERSION", "v1"),
        "HEAD_EPOCHS": os.environ.get("NIGHTLY_HEAD_EPOCHS", "5"),
        "FINETUNE_EPOCHS": os.environ.get("NIGHTLY_FINETUNE_EPOCHS", "3"),
        "TRAIN_BATCH_SIZE": os.environ.get("NIGHTLY_TRAIN_BATCH_SIZE", "8"),
        "PIPELINE_RUN_ID": RUN_ID,
    }
    print(
        f"Exec en {ML_CONTAINER}: train_resnet50 "
        f"(head={env['HEAD_EPOCHS']}, finetune={env['FINETUNE_EPOCHS']}, run={RUN_ID})"
    )
    exit_code, output = container.exec_run(cmd, environment=env, demux=False)
    if output:
        print(output.decode("utf-8", errors="replace"))
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
