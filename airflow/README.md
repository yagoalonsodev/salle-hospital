# Airflow — salle-hospital

**Estructura del módulo:** [`docs/estructura-repositorio.md`](../docs/estructura-repositorio.md#airflow--orquestación) — DAG en `airflow/dags/`, scripts compartidos en `scripts/`.

## UI

http://localhost:8081 — credenciales en `.env` (`AIRFLOW_ADMIN_USER`, `AIRFLOW_ADMIN_PASSWORD`; plantilla en `.env.example`).

## DAG `salle_rx_pipeline`

1. Comprueba `data/processed/watcher/pending.flag` (creado por el watcher).
2. Regenera `manifest.csv` y CSV clínico.
3. Lanza `ingest_validate_images.py` en `salle-pipeline` vía Docker API.
4. Borra el flag pendiente.

**Activar el DAG** en la UI (viene pausado por defecto) o:

```bash
docker exec salle-airflow airflow dags unpause salle_rx_pipeline
```

Programación: cada **15 minutos** (ajustable en el DAG).

## Logging

- Nivel **INFO** en consola y ficheros bajo `airflow/logs/`.
- Formato: `[YYYY-MM-DD HH:MM:SS] LEVEL [logger] — mensaje` (`airflow/config/log_config.py`).
- Metadatos de Airflow (BD interna) en volumen Docker `airflow_metadata`.

## Probar el flujo

```bash
docker compose up -d watcher airflow pipeline spark-master spark-worker postgres minio
docker exec salle-airflow airflow dags unpause salle_rx_pipeline

# Simular nueva imagen
cp data/raw/covid19_vs_pneumonia/train/NORMAL/alguna.jpg \
   data/raw/covid19_vs_pneumonia/incoming/train/NORMAL/nueva_prueba.jpg

# Forzar DAG o esperar schedule
docker exec salle-airflow airflow dags trigger salle_rx_pipeline
```

Ver logs del watcher: `docker logs -f salle-watcher`.

## MinIO — subida completa

`MAX_UPLOAD=0` en compose (Airflow + pipeline): cada ejecución sube **todas** las imágenes válidas al bucket, sin límite de prueba.
