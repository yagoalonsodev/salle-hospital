# Backlog — salle-hospital

Última actualización: 2026-05-16

Leyenda: `hecho` · `en curso` · `pendiente` · `bloqueado`

---

## Hecho

| ID | Tarea | Spec | Notas |
|----|-------|------|-------|
| D1-01 | Estructura monorepo (`api`, `ml`, `pipeline`, `dashboard`, `data`, `infra`) | — | Commit inicial |
| D1-02 | Documento de arquitectura y stack | — | `docs/architecture.md` |
| D1-03 | Docker Compose: Postgres, MinIO, Spark, Airflow | — | Apache Spark 3.5.3, Airflow standalone |
| D1-04 | Servicios app en compose (api, ml, dashboard, pipeline) | — | Stubs FastAPI / Streamlit |
| D1-05 | Init BD Airflow en Postgres | — | `infra/postgres/init-airflow-db.sql` |
| D1-06 | README y `.env.example` | — | Arranque `docker compose up -d --build` |
| D1-07 | Fix mount callback Docker Desktop (macOS) | — | Healthcheck API + depends_on dashboard |
| D1-08 | Skills Cursor: Diario IA + SDD | — | `.cursor/skills/` |
| D2-02 | Datos de ejemplo: RX en `raw/`, CSV clínico, manifest | [pipeline-datos-ejemplo.md](pipeline-datos-ejemplo.md) | 6432 JPG; `scripts/build_clinical_data.py` |
| D2-01 | Esquema PostgreSQL (pacientes, estudios, predicciones, pipeline) | [pipeline-esquema-db.md](pipeline-esquema-db.md) | `01-init-salle-schema.sql`, `docs/database-architecture.md` |

---

## En curso

| ID | Tarea | Spec | Notas |
|----|-------|------|-------|
| — | — | — | — |

---

## Pendiente — por fases (plan 1–10 mayo)

### Día 2–3 · Datos e ingesta

| ID | Tarea | Prioridad | Spec |
|----|-------|-----------|------|
| D2-03 | Job PySpark: ingesta CSV → Postgres | Alta | `pipeline-ingesta-csv.md` |
| D2-04 | Job PySpark: carga imágenes → MinIO + metadatos | Alta | `pipeline-ingesta-imagenes.md` |
| D2-05 | Validación calidad (incompletos, duplicados, corruptos) | Alta | `pipeline-calidad-datos.md` |

### Día 4–5 · ML (TensorFlow)

| ID | Tarea | Prioridad | Spec |
|----|-------|-----------|------|
| D4-01 | Investigación y elección de arquitectura CNN | Alta | `ml-arquitectura.md` |
| D4-02 | Preprocesado y augmentation de RX | Alta | `ml-preprocesado.md` |
| D4-03 | Entrenamiento clasificación 3 clases | Alta | `ml-entrenamiento.md` |
| D4-04 | Export SavedModel + servicio inferencia | Alta | `ml-servicio-inferencia.md` |
| D4-05 | Matriz de confusión y métricas | Media | `ml-evaluacion.md` |

### Día 6–7 · API e integración

| ID | Tarea | Prioridad | Spec |
|----|-------|-----------|------|
| D6-01 | Endpoints pacientes y estudios | Alta | `api-pacientes.md` |
| D6-02 | Endpoint predicción (proxy a ML + MinIO) | Alta | `api-predict.md` |
| D6-03 | Estado del pipeline y health agregado | Media | `api-pipeline-status.md` |

### Día 7–8 · Dashboard y automatización

| ID | Tarea | Prioridad | Spec |
|----|-------|-----------|------|
| D7-01 | Dashboard Streamlit (métricas, matriz confusión) | Alta | `dashboard-vista-clinica.md` |
| D7-02 | Alertas simuladas en dashboard | Media | `dashboard-alertas.md` |
| D8-01 | DAG Airflow: ingesta diaria | Alta | `airflow-dag-ingesta.md` |
| D8-02 | DAG Airflow: ETL Spark | Alta | `airflow-dag-etl.md` |
| D8-03 | DAG Airflow: inferencia batch ML | Alta | `airflow-dag-ml.md` |
| D8-04 | DAG Airflow: informes y alertas | Media | `airflow-dag-informes.md` |

### Día 9–10 · Documentación y cierre

| ID | Tarea | Prioridad | Spec |
|----|-------|-----------|------|
| D9-01 | Diario IA completo (entregable) | Alta | — |
| D9-02 | Memoria técnica | Alta | — |
| D9-03 | Consideraciones éticas y legales | Alta | `docs/etica.md` |
| D9-04 | Presentación 10–15 min | Alta | — |

---

## Bloqueado

| ID | Tarea | Motivo |
|----|-------|--------|
| — | — | — |
