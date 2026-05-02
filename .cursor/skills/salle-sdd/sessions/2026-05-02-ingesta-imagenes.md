# Sesión SDD — Ingesta, validación y deduplicación (2026-05-02)

> Commit: `33c9140` — 2026-05-02 11:00

## Flujo aplicado

1. BACKLOG **D2-04**, **D2-05** → spec `docs/specs/pipeline-ingesta-imagenes-calidad.md`
2. `pipeline/jobs/ingest_validate_images.py` + `db_log.py`
3. Salida en `data/processed/manifest/`; subida MinIO; log Postgres

## Pre-requisito de datos

215 ficheros `.jpg` no eran JPEG → `scripts/convert_rx_to_jpeg.py` (ver entrada diario 006).

## Artefactos

| Artefacto | Ruta |
|-----------|------|
| Spec | `docs/specs/pipeline-ingesta-imagenes-calidad.md` |
| Job | `pipeline/jobs/ingest_validate_images.py` |
