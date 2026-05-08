"""Callbacks Airflow → alertas en PostgreSQL."""

from __future__ import annotations

from db_alerts import create_alert


def record_task_failure(context) -> None:
    ti = context.get("task_instance")
    dag = context.get("dag")
    exc = context.get("exception")
    task_id = ti.task_id if ti else "unknown"
    dag_id = dag.dag_id if dag else "unknown"
    dag_run = context.get("dag_run")
    ref = dag_run.run_id if dag_run else None
    create_alert(
        title=f"Airflow: fallo en {dag_id}.{task_id}",
        message=str(exc)[:4000] if exc else "Error sin detalle",
        severity="critical",
        run_id=str(ref)[:32] if ref else None,
    )
