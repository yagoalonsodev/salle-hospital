#!/usr/bin/env python3
"""Ejecuta preprocesado Spark (features v1) en salle-pipeline — DAG reentrenamiento nocturno."""

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

PIPELINE_CONTAINER = os.environ.get("PIPELINE_CONTAINER", "salle-pipeline")
SPARK_MASTER = os.environ.get("SPARK_MASTER_URL", "spark://spark-master:7077")
RUN_ID = os.environ.get(
    "PIPELINE_RUN_ID",
    f"RUN-NT-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M')}-{uuid4().hex[:6]}",
)


def main() -> int:
    client = docker.from_env()
    try:
        container = client.containers.get(PIPELINE_CONTAINER)
    except docker.errors.NotFound:
        print(f"Contenedor no encontrado: {PIPELINE_CONTAINER}", file=sys.stderr)
        return 1

    cmd = [
        "/opt/spark/bin/spark-submit",
        "--master",
        SPARK_MASTER,
        "--driver-memory",
        "2g",
        "/opt/pipeline/jobs/preprocess_images.py",
    ]
    env = {
        "PIPELINE_RUN_ID": RUN_ID,
        "DATA_ROOT": os.environ.get("DATA_ROOT", "/opt/data"),
        "FEATURES_ROOT": os.environ.get(
            "FEATURES_ROOT", "/opt/data/processed/features"
        ),
        "FEATURES_VERSION": os.environ.get("FEATURES_VERSION", "v1"),
    }
    print(f"Exec en {PIPELINE_CONTAINER}: preprocess (run={RUN_ID})")
    exit_code, output = container.exec_run(cmd, environment=env)
    if output:
        print(output.decode("utf-8", errors="replace"))
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
