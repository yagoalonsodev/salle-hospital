FROM bitnami/spark:3.5

USER root
WORKDIR /opt/pipeline

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY jobs ./jobs

# Punto de entrada por definir (submit de jobs PySpark)
CMD ["sleep", "infinity"]
