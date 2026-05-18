FROM python:3.11-slim

WORKDIR /opt
RUN pip install --no-cache-dir pymongo>=4.6.0

COPY scripts/mongo_log_store.py scripts/log_sync_daemon.py scripts/salle_logging.py scripts/env_utils.py /opt/scripts/

ENV PYTHONPATH=/opt/scripts \
    SERVICE_NAME=log-sync \
    AIRFLOW_LOG_DIR=/opt/airflow/logs \
    EXTRA_LOG_DIRS=/opt/logs \
    LOG_SYNC_INTERVAL_SEC=60

CMD ["python3", "/opt/scripts/log_sync_daemon.py"]
