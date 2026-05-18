# Backlog — salle-hospital

Última actualización: 2026-05-14

Leyenda: `hecho` · `pendiente` · `bloqueado`

Estructura del repo: [`estructura-repositorio.md`](../estructura-repositorio.md)

---

## Hecho (Días 1–9 + cierre datos)

### Día 1 — Infra y arquitectura

| ID | Tarea | Spec / notas |
|----|-------|----------------|
| D1-01 | Monorepo (`api`, `ml`, `pipeline`, `dashboard`, `scripts`, `data`, `infra`) | `estructura-repositorio.md` |
| D1-02 | Documento arquitectura y stack | `architecture.md` |
| D1-03 | Docker Compose: Postgres, MinIO, Spark, Airflow | Spark 3.5.3 |
| D1-04 | Servicios app (api, ml, dashboard, pipeline) | — |
| D1-05 | Init BD Airflow | `infra/postgres/init-airflow-db.sql` |
| D1-06 | README y `.env.example` | — |
| D1-07 | Fix mount callback Docker Desktop | — |
| D1-08 | Skills Cursor (SDD, diario, seguridad) | `.cursor/skills/` |

### Día 2 — Datos e ingesta

| ID | Tarea | Spec / notas |
|----|-------|----------------|
| D2-01 | Esquema PostgreSQL | `pipeline-esquema-db.md`, `01-init-salle-schema.sql` |
| D2-02 | Datos ejemplo RX + CSV clínico | `pipeline-datos-ejemplo.md`, ~6433 JPG |
| D2-03 | Job PySpark ingesta CSV → Postgres | `pipeline-ingesta-csv.md`, `ingest_csv_to_postgres.py` |
| D2-04 | Ingesta imágenes → MinIO | `ingest_validate_images.py` |
| D2-05 | Validación y deduplicación | Parquet + `data_quality_issues` |
| D2-06 | Watcher RX + flag pendiente | `image_watcher.py` |
| D2-07 | Logging Airflow | `airflow/config/log_config.py` |
| D2-08 | Persistencia volúmenes Docker | `postgres_data`, `minio_data`, … |

### Día 3 — Preprocesado

| ID | Tarea | Spec / notas |
|----|-------|----------------|
| D3-01 | Resize y normalización 224×224 | `preprocess_images.py` |
| D3-02 | Data augmentation (train) | — |
| D3-03 | Split train / val / test | `features/v1/` |
| D3-04 | Spark + Pillow en workers | `infra/spark/Dockerfile` |

### Día 4–5 — ML

| ID | Tarea | Spec / notas |
|----|-------|----------------|
| D4-01 | Arquitectura CNN (ResNet50) | `ml-arquitectura.md`, comparativa 4 modelos |
| D4-02 | Preprocesado ML | Cubierto Día 3 |
| D4-03 | Entrenamiento 3 clases | `rx_resnet50_v1`, ~94 % test |
| D4-05 | Matriz confusión y métricas | `training_report_v1.json` |
| D5-01 | Informe comparativa arquitecturas | Notebook + JSON |
| D5-02 | Scripts entrenamiento unificados | `training_core.py` |
| D5-03 | Evaluación clínica FP/FN | `evaluacion-clinica-v1.md` |

### Día 6 — API Flask

| ID | Tarea | Spec / notas |
|----|-------|----------------|
| D6-01 | API + UI 3 pestañas | `api-predict.md` |
| D6-02 | Integración ML + Postgres + MinIO | — |
| D6-03 | Health agregado | `GET /health` |
| D6-04 | CRUD pacientes + sites | `api-pacientes.md` |
| D6-05 | Galería RX y resumen clínico | — |

### Día 7 — Dashboard

| ID | Tarea | Spec / notas |
|----|-------|----------------|
| D7-01 | Dashboard Streamlit | `dashboard-vista-clinica.md` |
| D7-02 | Alertas en dashboard | tabla `alerts` |
| D7-03 | Robustez API (logging, retry) | — |
| D7-04 | Estado pipeline en dashboard | `GET /api/dashboard` |

### Día 8 — Monitorización

| ID | Tarea | Spec / notas |
|----|-------|----------------|
| D8M-01 | Logging centralizado (+ MongoDB) | `salle_logging.py`, `mongo_log_store.py`, `log-sync` |
| D8M-02 | Calidad imágenes + auditoría BD | `data_quality_audit.py` |
| D8M-03 | Alertas pipeline / inferencia | `db_alerts.py`, Airflow callback |
| D8M-04 | Healthchecks Docker ampliados | compose |

### Día 9 — Documentación

| ID | Tarea | Spec / notas |
|----|-------|----------------|
| D9-01 | README completo | — |
| D9-02 | Memoria técnica | `memoria-tecnica.md` |
| D9-03 | Diagramas + ética (prompt injection) | `diagramas.md`, `etica.md` |
| D9-04 | Diario IA | `diario-ia/entradas/` |
| D9-05 | Estructura repo canónica | `estructura-repositorio.md` |

### Automatización (transversal)

| ID | Tarea | Spec / notas |
|----|-------|----------------|
| D8-01 | DAG `salle_rx_pipeline` | watcher → Spark → auditoría |

---

## Pendiente (opcional / Día 10)

| ID | Tarea | Prioridad | Notas |
|----|-------|-----------|-------|
| D10-01 | Presentación 10–15 min | Alta | Entregable enunciado |
| D10-02 | Demo `docker compose` desde cero ensayada | Alta | — |
| D4-04 | Export SavedModel estable en contenedor | Baja | `.h5` operativo |
| D8A-01 | DAG ETL Spark ampliado | Baja | Mejora post-MVP |
| D8A-02 | DAG inferencia batch ML | Baja | — |
| D8A-04 | DAG reentrenamiento nocturno 01:00 | Hecho | `salle_nightly_retrain`, [ml-retrain-nightly.md](ml-retrain-nightly.md) |
| D8A-03 | DAG informes automáticos | Baja | Dashboard cubre visualización |
| D6-06 | Endpoint dedicado estado pipeline en API | Baja | Parcial en `/api/dashboard` |

---

## Bloqueado

| ID | Tarea | Motivo |
|----|-------|--------|
| — | — | — |
