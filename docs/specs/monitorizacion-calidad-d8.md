# Spec: Monitorización y calidad de datos (Día 8)

| Meta | Valor |
|------|-------|
| Estado | implementado |
| Módulo | pipeline, api, ml, scripts, infra |
| BACKLOG | D8-01 … D8-04 |

## Objetivos

Sistema **robusto**: logging unificado, validación de imágenes y registros, alertas automáticas, healthchecks Docker y reintentos en servicios críticos.

## Componentes

| Área | Implementación |
|------|----------------|
| Logging | `scripts/salle_logging.py`, `api/app/logging_config.py`, `ml/app/logging_config.py` |
| Imágenes corruptas/incompletas | `ingest_validate_images.py` (Spark) + `data_quality_issues` |
| Registros incompletos | `scripts/data_quality_audit.py` → alertas |
| Alertas inferencia | `api/app/services/pipeline.py` + `alerts` |
| Alertas pipeline | `db_log.finish_run`, Airflow `on_failure_callback` |
| Alertas calidad | `db_alerts.alert_quality_batch` |
| Retry | `retry_util` (ML), `minio_store` (subida) |
| Healthchecks | postgres, api, ml, dashboard, airflow, minio, watcher |

## Criterios de aceptación

- [x] Logs estructurados en API, ML, watcher e ingesta
- [x] Rechazo de JPG corruptos y rutas incompletas en ingesta
- [x] Alertas visibles en dashboard (`alerts`)
- [x] Healthchecks en servicios principales del compose
- [x] Reintentos automáticos ML y MinIO

## Verificación

```bash
docker compose up -d
python3 scripts/data_quality_audit.py   # con DATABASE_URL
docker compose exec pipeline python3 /opt/scripts/data_quality_audit.py
```
