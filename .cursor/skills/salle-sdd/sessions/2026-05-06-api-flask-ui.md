# Sesión SDD — 2026-05-06 · API Flask, pacientes y UI radiografías (Día 6)

| Campo | Valor |
|-------|-------|
| Commit | _(rellenar tras `git log -1`)_ |
| BACKLOG | D6-01 … D6-05 |
| Specs | `docs/specs/api-predict.md`, `docs/specs/api-pacientes.md` |
| Diario | `docs/diario-ia/entradas/2026-05-06.md` |

## Alcance

- Sustituir stub FastAPI en `api/` por **Flask** (único framework HTTP del hospital).
- Microservicio **ML** (FastAPI) con inferencia ResNet50 (`rx_resnet50_v1.h5`).
- Endpoints `/health`, `/metrics`, `/upload`, `/predict`.
- CRUD `/api/patients`, catálogo `/api/sites`, imágenes `/api/studies/<id>/image`.
- UI web: Pacientes · Radiografías · Resumen.
- BD: `display_name`, tabla `sites`, estudios clínicos sin `label` ficticio.

## Estructura `api/app/`

| Capa | Contenido |
|------|-----------|
| `routes/` | HTTP fino (upload, patients, metrics, studies, sites, web) |
| `services/` | `pipeline.py`, `patients.py`, `ml_client.py`, `minio_store.py` |
| `repositories/` | SQL pacientes y sites |
| `templates/`, `static/` | Vista sin lógica de negocio |

## UI

- Crear paciente → flujo «Crear y subir radiografía».
- Galería RX del paciente (thumbnail desde MinIO, `study_id`, predicción).
- Resumen: cada fila con **ID estudio** y predicción debajo.
- Fix pestañas: quitar conflicto CSS `hidden` + `active`.

## Migraciones SQL

- `03-patients-display-name.sql`
- `04-sites-clinical-studies.sql`
- `05-remove-demo-rows.sql`

## Verificación

```bash
docker compose up -d --build postgres minio ml api
# http://localhost:8000/
curl -s http://localhost:8000/health
```

## Siguiente (Día 7)

- Dashboard Streamlit (`dashboard-vista-clinica.md`).
- DAGs ETL / ML batch en Airflow.
