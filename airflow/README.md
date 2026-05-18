# Airflow — salle-hospital

**Estructura del módulo:** [`docs/estructura-repositorio.md`](../docs/estructura-repositorio.md#airflow--orquestación) — DAG en `airflow/dags/`, scripts compartidos en `scripts/`.

## UI

http://localhost:8081 — credenciales en `.env` (`AIRFLOW_ADMIN_USER`, `AIRFLOW_ADMIN_PASSWORD`; plantilla en `.env.example`).

**Nota URL:** el puerto es **8081** en el Mac (mapeo `8081→8080` del contenedor), no `80:81` ni `8080` en el host.

### Safari / «conexión perdida» con el servidor

Tras un `docker compose down` sin borrar volúmenes, puede quedar un **PID viejo** del webserver y Gunicorn no arranca; el navegador muestra conexión reseteada. El `docker-compose.yml` borra esos PID al iniciar. Si aún falla: espera **1–3 minutos** tras el primer `up` (instala `_PIP_ADDITIONAL_REQUIREMENTS`), luego `docker compose restart airflow` y vuelve a abrir http://localhost:8081 .

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

## DAG `salle_nightly_retrain` (reentrenamiento 01:00)

Reentrena **ResNet50** con todas las imágenes en `data/raw/` (dataset original + nuevas del watcher):

1. `spark_preprocess_features` — PySpark `preprocess_images.py` → `data/processed/features/v1/`
2. `train_resnet50` — `train_resnet50.py` en `salle-ml` (épocas reducidas vía `.env`)
3. `reload_ml_service` — reinicia `salle-ml` para cargar el nuevo `.h5`

**No entrena en cada imagen nueva**; eso lo hace el watcher + `salle_rx_pipeline` (ingesta). Este DAG es un **batch diario** opcional.

```bash
docker exec salle-airflow airflow dags unpause salle_nightly_retrain
# Prueba manual (tarda mucho):
docker exec salle-airflow airflow dags trigger salle_nightly_retrain
```

| Variable | Default | Descripción |
|----------|---------|-------------|
| `NIGHTLY_RETRAIN_ENABLED` | `true` | `false` omite el DAG (ShortCircuit) |
| `NIGHTLY_HEAD_EPOCHS` | `5` | Épocas cabeza (menor que entrenamiento manual) |
| `NIGHTLY_FINETUNE_EPOCHS` | `3` | Fine-tuning |

Hora **01:00** = reloj del scheduler Airflow (por defecto **UTC**). Ajusta `AIRFLOW__CORE__DEFAULT_TIMEZONE` si necesitas hora local.

## Logging

- Nivel **INFO** en consola y ficheros bajo `airflow/logs/`.
- Formato: `[YYYY-MM-DD HH:MM:SS] LEVEL [logger] — mensaje` (`airflow/config/log_config.py`).
- Metadatos de Airflow (BD interna) en volumen Docker `airflow_metadata`.
- Copia periódica a **MongoDB** (`salle_logs.airflow_logs`) vía contenedor `salle-log-sync` — ver `README.md` raíz.

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
