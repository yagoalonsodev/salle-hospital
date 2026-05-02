"""
DAG: pipeline RX automatizado (watcher → manifest → Spark → limpiar pendiente).

Requiere: watcher activo, salle-pipeline en ejecución, docker.sock en Airflow.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator, ShortCircuitOperator

DATA_ROOT = Path(os.environ.get("DATA_ROOT", "/opt/data"))
PENDING_FLAG = DATA_ROOT / "processed/watcher/pending.flag"
SCRIPTS = Path(os.environ.get("AIRFLOW_SCRIPTS_DIR", "/opt/scripts"))

default_args = {
    "owner": "salle-hospital",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=2),
}


def _pending() -> bool:
    if not PENDING_FLAG.is_file():
        return False
    try:
        data = json.loads(PENDING_FLAG.read_text(encoding="utf-8"))
        return bool(data.get("pending", True))
    except json.JSONDecodeError:
        return True


def check_pending(**_context) -> bool:
    pending = _pending()
    if not pending:
        print("Sin imágenes pendientes; se omiten tareas de ingesta.")
    return pending


def clear_pending(**_context) -> None:
    if PENDING_FLAG.is_file():
        PENDING_FLAG.unlink()
        print("pending.flag eliminado.")


def run_spark_ingest(**_context) -> None:
    script = SCRIPTS / "airflow_trigger_ingest.py"
    result = subprocess.run(
        [sys.executable, str(script)],
        check=False,
        capture_output=True,
        text=True,
    )
    print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    if result.returncode != 0:
        raise RuntimeError(f"spark ingest falló con código {result.returncode}")


with DAG(
    dag_id="salle_rx_pipeline",
    default_args=default_args,
    description="Ingesta RX si el watcher marcó imágenes nuevas",
    schedule_interval=timedelta(minutes=15),
    start_date=datetime(2026, 5, 2),
    catchup=False,
    tags=["salle", "rx", "ingesta"],
) as dag:
    gate = ShortCircuitOperator(
        task_id="check_pending_images",
        python_callable=check_pending,
    )

    rebuild_manifest = BashOperator(
        task_id="rebuild_manifest",
        bash_command=f"python3 {SCRIPTS}/build_clinical_data.py",
    )

    spark_ingest = PythonOperator(
        task_id="spark_ingest_images",
        python_callable=run_spark_ingest,
    )

    clear_flag = PythonOperator(
        task_id="clear_pending_flag",
        python_callable=clear_pending,
    )

    gate >> rebuild_manifest >> spark_ingest >> clear_flag
