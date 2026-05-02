# Sesión SDD — Datos de ejemplo y CSV clínico (2026-05-02)

> Commit: `fda8c86` — 2026-05-02 09:00 (mismo commit que esquema BD)

## Flujo aplicado

1. BACKLOG **D2-02** → spec `docs/specs/pipeline-datos-ejemplo.md`
2. Dataset RX en `data/raw/covid19_vs_pneumonia/` (6432 JPG, 3 clases)
3. `scripts/build_clinical_data.py` → `manifest.csv`, `studies.csv`, `pipeline_events.csv`
4. BACKLOG: D2-02 → **hecho**

## Artefactos

| Artefacto | Ruta |
|-----------|------|
| Spec | `docs/specs/pipeline-datos-ejemplo.md` |
| Script | `scripts/build_clinical_data.py` |
| Doc datos | `data/README.md` |

## Relacionado

- Esquema Postgres del mismo commit: [2026-05-02-esquema-db.md](2026-05-02-esquema-db.md)
