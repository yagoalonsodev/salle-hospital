"""Logging Airflow: formato legible y persistencia en airflow/logs/."""

from copy import deepcopy

from airflow.config_templates.airflow_local_settings import DEFAULT_LOGGING_CONFIG

LOGGING_CONFIG = deepcopy(DEFAULT_LOGGING_CONFIG)

LOGGING_CONFIG["formatters"]["airflow"] = {
    "format": "[%(asctime)s] %(levelname)s [%(name)s] — %(message)s",
    "datefmt": "%Y-%m-%d %H:%M:%S",
}
LOGGING_CONFIG["formatters"]["airflow.task"] = {
    "format": "[%(asctime)s] %(levelname)s [%(task_id)s] — %(message)s",
    "datefmt": "%Y-%m-%d %H:%M:%S",
}

for handler in ("console", "task", "processor"):
    key = f"{handler}_default" if handler != "console" else "console"
    if key in LOGGING_CONFIG.get("handlers", {}):
        LOGGING_CONFIG["handlers"][key].setdefault(
            "formatter", "airflow.task" if handler == "task" else "airflow"
        )
