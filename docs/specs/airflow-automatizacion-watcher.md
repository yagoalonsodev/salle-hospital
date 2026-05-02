# Spec: Automatización — watcher de imágenes y pipeline Airflow

| Meta | Valor |
|------|-------|
| Estado | implementado |
| Módulo | airflow / scripts / infra |
| BACKLOG | D2-06, D2-07, D8-01 (parcial) |

## 1. Descripción funcional

- **Watcher**: vigila `data/raw/covid19_vs_pneumonia/incoming/`; al detectar `.jpg` nuevos, registra evento, mueve a `train/{NORMAL|PNEUMONIA|COVID19}/` y marca ingesta pendiente.
- **Airflow**: DAG programado que, si hay pendientes, regenera manifest y lanza el job PySpark en `salle-pipeline` vía Docker API.
- **Logging Airflow**: nivel INFO, formato legible, logs en volumen/bind `airflow/logs`.
- **Persistencia**: volúmenes nombrados para metadatos Airflow y estado del watcher.

## 2. Inputs / outputs

| Input | Origen |
|-------|--------|
| Nuevas `.jpg` en `incoming/` | Simulación de llegada de RX |
| Estado `pending.flag` | Watcher |

| Output | Destino |
|--------|---------|
| Imagen en árbol `train|test/CLASE/` | `data/raw/` |
| `events.jsonl`, `pending.flag` | `data/processed/watcher/` |
| Logs DAG | `airflow/logs/` |
| Parquet / MinIO / Postgres | Job Spark existente |

## 3. Criterios de aceptación

- [x] Copiar una imagen a `incoming/train/NORMAL/` la incorpora al árbol y deja `pending.flag`.
- [x] DAG `salle_rx_pipeline` ejecuta ingesta Spark si hay pendientes.
- [x] Logs Airflow visibles en UI y en `airflow/logs/`.
- [x] `docker compose down` no borra Postgres, MinIO, metadatos Airflow ni estado watcher (volúmenes).
- [x] `MAX_UPLOAD=0`: subida de **todas** las imágenes válidas a MinIO (sin límite de prueba).

## 4. Prompt base

```text
Implementar watcher de nuevas imágenes, logging básico Airflow, DAG de pipeline
y volúmenes Docker para persistencia; documentar en SDD y diario.
```
