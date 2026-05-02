# Sesión SDD — Watcher, Airflow y persistencia Docker (2026-05-02)

> Commit: `9848819` — 2026-05-02 14:00  
> Spec: `docs/specs/airflow-automatizacion-watcher.md`

## Entregables

| Artefacto | Ruta |
|-----------|------|
| Watcher | `scripts/image_watcher.py`, `scripts/watcher_state.py`, `salle-watcher` |
| DAG | `airflow/dags/salle_rx_pipeline.py` |
| Trigger Spark | `scripts/airflow_trigger_ingest.py` |
| Logging | `airflow/config/log_config.py` |
| Compose | `airflow_metadata`, `MAX_UPLOAD=0` (subida completa MinIO) |

## Flujo verificado

1. Imagen en `incoming/train/PNEUMONIA/` → watcher → `raw/` + `pending.flag`
2. DAG `salle_rx_pipeline` → manifest → Spark → MinIO (6399 objetos) → clear flag

## BACKLOG

D2-06, D2-07, D2-08, D8-01 (parcial) → **hecho**
