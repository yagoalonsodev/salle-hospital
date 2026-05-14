# Memoria técnica — laSalle Health Center

| Campo | Valor |
|-------|-------|
| Proyecto | `salle-hospital` |
| Cliente simulado | laSalle Health Center |
| Autores | Equipo práctica Máster |
| Versión documento | 1.0 — mayo 2026 |
| Repositorio | `practica-tocha` |

---

## Resumen ejecutivo

Se ha implementado una plataforma de **soporte hospitalario** que integra **Big Data** (Apache Spark, PostgreSQL, MinIO), **orquestación** (Apache Airflow), **Deep Learning** (TensorFlow / ResNet50 para radiografías de tórax) y **capa de aplicación** (API Flask, dashboard Streamlit). El sistema clasifica radiografías en tres clases — **sana**, **neumonía** y **COVID-19** — con precisión de test ~94 % (ResNet50 v1), expone resultados vía API y dashboard, y automatiza la ingesta de nuevas imágenes mediante watcher + DAG.

El desarrollo siguió **Spec-Driven Development (SDD)** con Cursor; el proceso queda documentado en [`docs/diario-ia/`](diario-ia/).

---

## 1. Contexto y objetivos

El hospital necesita explotar datos clínicos e imágenes RX para:

1. Centralizar ingesta y calidad de datos.
2. Clasificar radiografías con IA como apoyo (no diagnóstico definitivo).
3. Automatizar pipelines repetitivos.
4. Visualizar métricas y alertas operativas.

**Alcance MVP cumplido:** ingesta masiva y por watcher, preprocesado, entrenamiento e inferencia, API con UI web, dashboard analítico, monitorización (Día 8) y documentación (Día 9).

Detalle del encargo: [`enunciado.md`](../enunciado.md) (local).

Organización del código: [`estructura-repositorio.md`](estructura-repositorio.md) (árbol canónico de carpetas).

---

## 2. Arquitectura del sistema

### 2.1 Vista general

Ver diagramas en [`diagramas.md`](diagramas.md) y [`architecture.md`](architecture.md).

| Capa | Tecnología | Rol |
|------|------------|-----|
| Presentación | HTML/JS + Streamlit | UI clínica y dashboard |
| API | **Flask** (Gunicorn) | REST, orquestación, validación |
| IA | TensorFlow 2.x + FastAPI interno | Inferencia ResNet50 |
| Big Data | PySpark 3.5 | ETL, validación, preprocesado |
| Orquestación | Airflow 2.10 | DAG `salle_rx_pipeline` |
| Datos | PostgreSQL 16, MinIO | Relacional + objetos S3 |
| Infra | Docker Compose | 11+ servicios reproducibles |

> **Nota:** La API hospitalaria es **Flask** (`api/`). El servicio `ml/` expone **FastAPI** solo para inferencia del modelo.

### 2.2 Flujo de datos

```
Fuentes (CSV, JPG) → Watcher / Spark ingesta → PostgreSQL + MinIO
                              ↓
                    Airflow (cada 15 min si hay pendiente)
                              ↓
              Preprocesado features/v1 → Entrenamiento offline
                              ↓
         Upload clínico → API → ML → predictions → Dashboard
```

---

## 3. Pipeline de datos (Big Data)

### 3.1 Datos de ejemplo

- **6.433** radiografías JPG en `data/raw/covid19_vs_pneumonia/`.
- Manifest y CSV clínico generados con `scripts/build_clinical_data.py`.
- Esquema PostgreSQL: `infra/postgres/01-init-salle-schema.sql` (+ migraciones 03–05).

### 3.2 Ingesta y calidad (Spark)

Job: `pipeline/jobs/ingest_validate_images.py`

| Validación | Acción |
|------------|--------|
| JPG corrupto | Magic bytes `FF D8 FF`, tamaño mínimo |
| Registro incompleto | `path_ok`, split/label válidos |
| Duplicados | MD5 + ventana Spark |

Salidas: `validated.parquet`, `rejected.parquet`, filas en `data_quality_issues`.

### 3.3 Preprocesado (Día 3)

`pipeline/jobs/preprocess_images.py` — resize 224×224, normalización, augmentation en train, splits train/val/test → `data/processed/features/v1/`.

### 3.4 Automatización

- **Watcher:** `scripts/image_watcher.py` vigila `incoming/`.
- **Airflow:** DAG `salle_rx_pipeline` — manifest → Spark → limpiar flag → auditoría BD.
- UI Airflow: http://localhost:8081 (`admin` / ver `.env`).

---

## 4. Modelo de inteligencia artificial

### 4.1 Problema y clases

Clasificación multiclase de radiografías de tórax: **sana**, **neumonía**, **covid**.

### 4.2 Arquitectura elegida

- **Transfer learning** con **ResNet50** (ImageNet), cabeza densa 3 clases.
- Comparativa Día 5: ResNet50, EfficientNetB0, DenseNet121, CNN baseline — ver `ml/models/reports/architecture_comparison.json`.

### 4.3 Resultados (v1)

| Métrica | Valor aprox. |
|---------|----------------|
| Accuracy test | ~94 % |
| Artefacto | `ml/models/rx_resnet50_v1.h5` |
| Informe | `docs/ml/resultados-entrenamiento-v1.md` |
| Evaluación clínica | `docs/ml/evaluacion-clinica-v1.md` (FN neumonía) |

### 4.4 Servicio de inferencia

- Contenedor `ml` en puerto **8001**.
- API Flask llama a ML con **reintentos** (3) y registra alertas si falla.

---

## 5. API y aplicación web (Día 6)

### 5.1 Endpoints principales

| Método | Ruta | Función |
|--------|------|---------|
| GET | `/health` | Estado API, BD, MinIO, ML |
| POST | `/upload` | Subir RX + predicción |
| GET | `/api/patients` | CRUD pacientes |
| GET | `/api/dashboard` | Agregados para Streamlit |
| GET | `/api/studies/<id>/image` | Proxy imagen MinIO |

### 5.2 Capas (SDD)

`routes/` → `services/` → `repositories/` — ver [`specs/api-predict.md`](specs/api-predict.md).

### 5.3 UI

Tres pestañas: Pacientes, Radiografías (galería), Resumen. JavaScript modular en `api/app/static/js/`.

---

## 6. Dashboard (Día 7)

- **Streamlit** en http://localhost:8501.
- Métricas IA, distribución por clase, matriz de confusión (informe JSON), pipeline runs, tabla `alerts`.
- Consume solo `GET /api/dashboard` (sin acceso directo a BD).

---

## 7. Monitorización y robustez (Día 8)

| Capacidad | Implementación |
|-----------|----------------|
| Logging | `salle_logging.py`, `logging_config` API/ML |
| Alertas | Tabla `alerts`, `db_alerts.py`, callback Airflow |
| Auditoría BD | `data_quality_audit.py` |
| Healthchecks | postgres, api, ml, dashboard, minio, spark, watcher, pipeline |
| Retry | ML client, MinIO upload |

Spec: [`specs/monitorizacion-calidad-d8.md`](specs/monitorizacion-calidad-d8.md).

---

## 8. Desarrollo asistido por IA (Vibe Coding)

Herramienta: **Cursor** con skills `@salle-sdd` y `@diario-ia`.

| Aspecto | Práctica adoptada |
|---------|-------------------|
| Specs antes de código | `docs/specs/*.md`, BACKLOG |
| Prompts literales | Guardados en `docs/diario-ia/entradas/` |
| Corrección humana | Revisión de diffs, pruebas Docker, fixes UX |
| Errores documentados | Ver diario Día 6–9 (paneles UI, Streamlit CMD, etc.) |

Índice completo: [`diario-ia/INDEX.md`](diario-ia/INDEX.md).

---

## 9. Ética, legal y Prompt Injection

Análisis detallado: [`etica.md`](etica.md).

Incluye:

1. **Prompt injection en informes médicos** — texto malicioso en ficheros; mitigación: sanitización, separación prompt/datos.
2. **Prompt injection en chatbot clínico** — extracción de datos; mitigación: RBAC, filtrado, validación API.

La inferencia actual **no usa LLM generativo**; el riesgo principal en MVP es de **fuga de datos vía API** (mitigado con capas y futuro RBAC).

---

## 10. Despliegue y operación

```bash
cp .env.example .env
docker compose up -d --build
```

Servicios y credenciales: [`README.md`](../README.md).

Volúmenes persistentes: `postgres_data`, `minio_data`, `airflow_metadata`, bind `./data`.

---

## 11. Limitaciones y trabajo futuro

| Limitación | Mejora propuesta |
|------------|------------------|
| DAG solo ingesta RX | DAGs ETL CSV, inferencia batch (BACKLOG D8A-*) |
| Sin RBAC en API | Roles médico/admin + OAuth2 |
| Modelo con FN en neumonía | Reentrenamiento, threshold por clase |
| LLM / chatbot no implementado | Si se añade, aplicar `etica.md` §3 |

---

## 12. Referencias documentales

| Documento | Contenido |
|-----------|-----------|
| [estructura-repositorio.md](estructura-repositorio.md) | Árbol de carpetas |
| [architecture.md](architecture.md) | Decisiones de stack |
| [database-architecture.md](database-architecture.md) | Esquema ER |
| [diagramas.md](diagramas.md) | Mermaid exportables |
| [etica.md](etica.md) | Ética + prompt injection |
| [specs/BACKLOG.md](specs/BACKLOG.md) | Estado de tareas |
| [ml/resultados-entrenamiento-v1.md](ml/resultados-entrenamiento-v1.md) | Métricas ML |

---

## 13. Cumplimiento del encargo (`enunciado.md`)

| Requisito del enunciado | Estado | Evidencia en el repo |
|-------------------------|--------|----------------------|
| Modelo IA justificado (clasificación RX 3 clases) | **Cumple** | `docs/ml/arquitectura-rx.md`, ResNet50, comparativa Día 5 |
| Big Data: volumen + no estructurado + multi-fuente | **Cumple** | ~6.4k JPG, CSV clínico, MinIO + Postgres |
| Pipeline: ingesta → limpieza → transformación → análisis | **Cumple** | `pipeline/jobs/`, specs en `docs/specs/` |
| Automatización (informes, alertas, ficheros, ingesta) | **Cumple** | Watcher, Airflow DAG, tabla `alerts`, dashboard |
| Visualización (gráficos, dashboard) | **Cumple** | Streamlit `:8501`, UI Flask |
| Docker Compose, un comando | **Cumple** | `docker compose up -d --build`, `README.md` |
| Postgres + almacén no estructurado (MinIO) | **Cumple** | `docker-compose.yml`, `docs/database-architecture.md` |
| Framework escalable (PySpark) + justificación | **Cumple** | `docs/preprocess-distributed-justification.md` |
| Logging, calidad, alertas | **Cumple** | Día 8, `docs/specs/monitorizacion-calidad-d8.md` |
| SDD + specs antes de código | **Cumple** | `docs/specs/`, `.cursor/skills/salle-sdd/` |
| Diario IA (prompts, iteraciones, reflexión) | **Cumple** | `docs/diario-ia/` |
| Matriz confusión + reflexión clínica FP/FN | **Cumple** | `docs/ml/evaluacion-clinica-v1.md`, informes |
| Ética y legal (sesgos, privacidad, riesgos) | **Cumple** | `docs/etica.md` (+ prompt injection) |
| Memoria técnica (apartados del enunciado) | **Cumple** | Este documento |
| Código organizado | **Cumple** | `docs/estructura-repositorio.md` |
| Presentación 10–15 min | **Pendiente** | Día 10 (guion en conversación / por entregar) |
| Ingesta CSV clínico → Postgres (Spark batch) | **Sí** | `ingest_csv_to_postgres.py` (D2-03) |
| Informes PDF automáticos | **Parcial** | Métricas en dashboard; sin generador PDF |
| Email simulado en alertas | **Parcial** | Alertas en BD + dashboard (no SMTP) |
| SavedModel en contenedor ML | **Parcial** | `.h5` operativo; export SavedModel documentado como pendiente |

**Conclusión:** el MVP del encargo está **sustancialmente cubierto** para entrega y demo. Los ítems *parcial* son mejoras explícitas en BACKLOG o documentación, no bloquean la defensa del proyecto si se mencionan como limitaciones.

---

*Documento generado como entregable Día 9 — Documentación y memoria técnica (mayo 2026).*
