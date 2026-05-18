"""
DAG: reentrenamiento nocturno ResNet50 (01:00).

Preprocesa todas las RX en data/raw → features/v1 → entrena → reinicia ML.
Activar en la UI o: airflow dags unpause salle_nightly_retrain
"""

from __future__ import annotations

import os
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path

from airflow import DAG
from airflow.operators.python import PythonOperator, ShortCircuitOperator

DATA_ROOT = Path(os.environ.get("DATA_ROOT", "/opt/data"))
FEATURES_DIR = (
    Path(os.environ.get("FEATURES_ROOT", str(DATA_ROOT / "processed/features")))
    / os.environ.get("FEATURES_VERSION", "v1")
)
RAW_RX = DATA_ROOT / "raw/covid19_vs_pneumonia"
SCRIPTS = Path(os.environ.get("AIRFLOW_SCRIPTS_DIR", "/opt/scripts"))

if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from airflow_callbacks import record_task_failure  # noqa: E402

default_args = {
    "owner": "salle-hospital",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 0,
    "on_failure_callback": record_task_failure,
}


def _run_script(name: str) -> None:
    script = SCRIPTS / name
    result = subprocess.run(
        [sys.executable, str(script)],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    if result.returncode != 0:
        raise RuntimeError(f"{name} falló con código {result.returncode}")


def check_retrain_enabled(**_context) -> bool:
    flag = os.environ.get("NIGHTLY_RETRAIN_ENABLED", "true").lower()
    if flag in ("0", "false", "no", "off"):
        print("NIGHTLY_RETRAIN_ENABLED=false; se omite reentrenamiento.")
        return False
    return True


def check_raw_data(**_context) -> bool:
    if not RAW_RX.is_dir():
        print(f"No existe {RAW_RX}; nada que preprocesar.")
        return False
    jpgs = list(RAW_RX.rglob("*.jpg")) + list(RAW_RX.rglob("*.jpeg"))
    if not jpgs:
        print("Sin imágenes .jpg en raw; se omite reentrenamiento.")
        return False
    print(f"Imágenes en raw: {len(jpgs)}")
    return True


def run_preprocess(**_context) -> None:
    _run_script("airflow_trigger_preprocess.py")


def run_train(**_context) -> None:
    _run_script("airflow_trigger_train.py")


def run_reload_ml(**_context) -> None:
    _run_script("airflow_reload_ml.py")


with DAG(
    dag_id="salle_nightly_retrain",
    default_args=default_args,
    description="Preprocesado + entrenamiento ResNet50 diario (01:00)",
    schedule_interval="0 1 * * *",
    start_date=datetime(2026, 5, 18),
    catchup=False,
    tags=["salle", "ml", "retrain"],
    max_active_runs=1,
) as dag:
    gate_enabled = ShortCircuitOperator(
        task_id="check_retrain_enabled",
        python_callable=check_retrain_enabled,
    )
    gate_data = ShortCircuitOperator(
        task_id="check_raw_data",
        python_callable=check_raw_data,
    )
    preprocess = PythonOperator(
        task_id="spark_preprocess_features",
        python_callable=run_preprocess,
        execution_timeout=timedelta(hours=4),
    )
    train = PythonOperator(
        task_id="train_resnet50",
        python_callable=run_train,
        execution_timeout=timedelta(hours=12),
    )
    reload_ml = PythonOperator(
        task_id="reload_ml_service",
        python_callable=run_reload_ml,
    )

    gate_enabled >> gate_data >> preprocess >> train >> reload_ml
