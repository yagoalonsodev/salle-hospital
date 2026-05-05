# Backlog — salle-hospital

Última actualización: 2026-05-05

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
| D2-04 | Carga automática imágenes → MinIO | [pipeline-ingesta-imagenes-calidad.md](pipeline-ingesta-imagenes-calidad.md) | `jobs/ingest_validate_images.py` |
| D2-05 | Validación y deduplicación (calidad) | [pipeline-ingesta-imagenes-calidad.md](pipeline-ingesta-imagenes-calidad.md) | Parquet validated/rejected + Postgres |
| D2-06 | Watcher de nuevas imágenes RX | [airflow-automatizacion-watcher.md](airflow-automatizacion-watcher.md) | `salle-watcher`, `incoming/` |
| D2-07 | Logging básico Airflow | [airflow-automatizacion-watcher.md](airflow-automatizacion-watcher.md) | `airflow/config/log_config.py` |
| D2-08 | Persistencia Docker (volúmenes) | [airflow-automatizacion-watcher.md](airflow-automatizacion-watcher.md) | `postgres_data`, `minio_data`, `airflow_metadata` |
| D8-01 | DAG pipeline RX automatizado | [airflow-automatizacion-watcher.md](airflow-automatizacion-watcher.md) | `salle_rx_pipeline` (parcial: ingesta) |
| D3-01 | Preprocesado RX: resize, normalización | [pipeline-preprocesado-imagenes.md](pipeline-preprocesado-imagenes.md) | `preprocess_images.py`, 224×224 |
| D3-02 | Data augmentation (rot, flip, zoom) | [pipeline-preprocesado-imagenes.md](pipeline-preprocesado-imagenes.md) | Solo split train |
| D3-03 | Split train / validation / test | [pipeline-preprocesado-imagenes.md](pipeline-preprocesado-imagenes.md) | 6399 → 19446 muestras en `features/v1/` |
| D3-04 | Imagen Spark con Pillow en workers | [pipeline-preprocesado-imagenes.md](pipeline-preprocesado-imagenes.md) | `infra/spark/Dockerfile` |
| D4-01 | Investigación y elección de arquitectura CNN | [ml-arquitectura.md](ml-arquitectura.md) | TL + ResNet50; `docs/ml/arquitectura-rx.md` |
| D4-02 | Preprocesado y augmentation de RX (ML) | [pipeline-preprocesado-imagenes.md](pipeline-preprocesado-imagenes.md) | Cubierto en Día 3 (`features/v1/`) |
| D4-03 | Entrenamiento clasificación 3 clases | [ml-entrenamiento.md](ml-entrenamiento.md) | `rx_resnet50_v1`, test acc ~94 % post fine-tune |
| D4-05 | Matriz de confusión y métricas | [ml-entrenamiento.md](ml-entrenamiento.md) | `reports/training_report_v1.json` |
| D5-01 | Informe comparativa 4 arquitecturas | [ml-entrenamiento.md](ml-entrenamiento.md) | Notebook + `architecture_comparison.json` |
| D5-02 | Scripts entrenamiento unificados | [ml-entrenamiento.md](ml-entrenamiento.md) | `training_core.py`, `train_*`, `train_compare_architectures.py` |
| D5-03 | Documentación resultados y evaluación clínica | [ml-entrenamiento.md](ml-entrenamiento.md) | `docs/ml/resultados-entrenamiento-v1.md`, `evaluacion-clinica-v1.md` |

---

## En curso

| ID | Tarea | Spec | Notas |
|----|-------|------|-------|
| D2-03 | Job PySpark: ingesta CSV → Postgres | `pipeline-ingesta-csv.md` | Siguiente prioridad datos |

---

## Pendiente — por fases (plan 1–10 mayo)

### Día 2–3 · Datos e ingesta

| ID | Tarea | Prioridad | Spec |
|----|-------|-----------|------|
| D2-03 | Job PySpark: ingesta CSV → Postgres | Alta | `pipeline-ingesta-csv.md` (pendiente) |

### Día 4–5 · ML (TensorFlow)

| ID | Tarea | Prioridad | Spec |
|----|-------|-----------|------|
| D4-04 | Export SavedModel + servicio inferencia | Alta | `ml-servicio-inferencia.md` (SavedModel pendiente en macOS; `.h5` listo) |

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
| D8-01 | DAG Airflow: ingesta diaria | Alta | Cubierto por `salle_rx_pipeline`; ampliar en `airflow-dag-ingesta.md` |
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
