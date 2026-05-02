# Sesión SDD — Verificación Postgres + MinIO (2026-05-02)

> Commit del script de verificación E2E (2 mayo, mañana).

## Objetivo

Comprobar encargo: Postgres + MinIO, calidad, trazabilidad en `pipeline_runs` / `pipeline_events`.

## Pasos

1. `spark-submit` → `ingest_validate_images.py`
2. `scripts/verify_pipeline_integration.py` en `salle-pipeline`

## Resultado (tras conversión JPEG)

- 6432 JPEG válidos; rechazos esperados solo por duplicados MD5 (~32).
- Postgres y MinIO OK en prueba con `RUN-VERIFY-IMG-01`.
