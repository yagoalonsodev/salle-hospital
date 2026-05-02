FROM python:3.11-slim

WORKDIR /opt
COPY scripts/requirements-watcher.txt /tmp/requirements-watcher.txt
RUN pip install --no-cache-dir -r /tmp/requirements-watcher.txt

COPY scripts/watcher_state.py scripts/image_watcher.py /opt/scripts/

ENV DATA_ROOT=/opt/data \
    WATCH_INCOMING_DIR=/opt/data/raw/covid19_vs_pneumonia/incoming

CMD ["python3", "/opt/scripts/image_watcher.py"]
