# Sesión SDD — Eliminar patients.csv (2026-05-02)

> Commit: `77607d0` — 2026-05-02 10:00

## Decisión

El dataset RX ya aporta las 3 clases. `patients.csv` con sexo/edad inventados no aporta al ML ni al encargo; se elimina el fichero.

## Cambios

| Artefacto | Acción |
|-----------|--------|
| `scripts/build_clinical_data.py` | Solo `manifest.csv`, `studies.csv`, `pipeline_events.csv` |
| `data/raw/clinical/patients.csv` | Eliminado |
| `docs/specs/pipeline-datos-ejemplo.md` | Actualizado |
| `docs/database-architecture.md` | Ingesta: `patients` desde `patient_id` en `studies.csv` |
| `data/README.md` | Árbol sin patients.csv |

## Postgres

Tabla `patients` se mantiene (FK). Job D2-03: `INSERT` mínimo por `patient_id` distinto al cargar `studies`.

## BACKLOG

Sin cambio de ID; nota en D2-02: sin CSV de pacientes falsos.
