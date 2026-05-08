FROM python:3.11-slim

WORKDIR /opt
COPY scripts/requirements-watcher.txt /tmp/requirements-watcher.txt
RUN pip install --no-cache-dir -r /tmp/requirements-watcher.txt

ENV DATA_ROOT=/opt/data \
    WATCH_INCOMING_DIR=/opt/data/raw/covid19_vs_pneumonia/incoming \
    WATCHER_HEARTBEAT=/tmp/watcher-heartbeat

CMD ["python3", "/opt/scripts/image_watcher.py"]
