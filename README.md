# salle-hospital — laSalle Health Center

Sistema inteligente de soporte hospitalario: pipeline Big Data, clasificación de radiografías de tórax (**Sana / Neumonía / COVID-19**), API clínica y dashboard operativo.

**Documentación principal:** [Memoria técnica](docs/memoria-tecnica.md) · [Diagramas](docs/diagramas.md) · [Ética y Prompt Injection](docs/etica.md) · [Diario IA](docs/diario-ia/)

---

## Stack

| Componente | Tecnología | Puerto |
|------------|------------|--------|
| API + UI web | **Flask** (Gunicorn) | 8000 |
| Inferencia ML | TensorFlow + **FastAPI** | 8001 |
| Big Data | Apache Spark (PySpark 3.5) | 7077 / UI 8080 |
| Orquestación | Apache Airflow 2.10 | 8081 |
| Base de datos | PostgreSQL 16 | 5432 |
| Objetos (RX) | MinIO (S3) | 9000 / consola 9001 |
| Dashboard | Streamlit | 8501 |
| Infra | Docker Compose | — |

---

## Arranque rápido

```bash
cp .env.example .env
docker compose up -d --build
```

> Si PostgreSQL ya existía sin la BD `airflow`:  
> `docker compose down -v && docker compose up -d --build`

### URLs y credenciales

| Servicio | URL | Acceso |
|----------|-----|--------|
| **UI hospital (Flask)** | http://localhost:8000 | Pacientes, upload RX, resumen |
| **API health** | http://localhost:8000/health | — |
| **ML** | http://localhost:8001/health | — |
| **Dashboard Streamlit** | http://localhost:8501 | Métricas, alertas, pipeline |
| **Airflow** | http://localhost:8081 | `.env` → `AIRFLOW_ADMIN_USER` / `AIRFLOW_ADMIN_PASSWORD` (por defecto `admin` / `Admin123.`) |
| **MinIO consola** | http://localhost:9001 | `.env` → `MINIO_ROOT_*` |
| **Spark Master UI** | http://localhost:8080 | — |
| **PostgreSQL** | `localhost:5432` | `.env` → `POSTGRES_*` |

---

## Estructura del repositorio

```
├── api/              # Flask: REST + UI (templates, static/js)
├── ml/               # TensorFlow: entrenamiento (scripts/) + inferencia (app/)
├── pipeline/         # Jobs PySpark (ingesta, preprocesado)
├── dashboard/        # Streamlit
├── airflow/dags/     # DAG salle_rx_pipeline
├── scripts/          # Watcher, utilidades, alertas
├── data/             # Raw / processed (bind mount)
├── docs/             # Memoria, specs SDD, diario IA
├── infra/            # Postgres, Spark, watcher
└── docker-compose.yml
```

---

## Flujo operativo

```mermaid
flowchart LR
    RX[RX en incoming/] --> W[Watcher]
    W --> AF[Airflow DAG]
    AF --> SP[Spark ingesta]
    SP --> DB[(PostgreSQL)]
    SP --> S3[(MinIO)]
    U[Usuario] --> API[Flask API]
    API --> ML[TensorFlow]
    ML --> DB
    DASH[Streamlit] --> API
```

1. **Batch:** imágenes en `data/raw/` → job Spark → MinIO + calidad en BD.  
2. **Automático:** copiar JPG a `data/raw/covid19_vs_pneumonia/incoming/train/NORMAL/` → watcher → DAG cada 15 min.  
3. **Clínico:** subir RX en http://localhost:8000 → predicción → ver en dashboard.

Detalle watcher: [`airflow/README.md`](airflow/README.md).

### Automatización

```bash
docker compose up -d watcher airflow pipeline spark-master spark-worker
docker exec salle-airflow airflow dags unpause salle_rx_pipeline
```

---

## Entrenamiento del modelo (offline)

```bash
docker compose build ml
docker compose run --rm --no-deps \
  -v ./data:/opt/data -v ./ml/models:/app/models \
  -e FEATURES_ROOT=/opt/data/processed/features \
  ml python scripts/train_resnet50.py
```

Resultados: [`docs/ml/resultados-entrenamiento-v1.md`](docs/ml/resultados-entrenamiento-v1.md) · evaluación clínica: [`docs/ml/evaluacion-clinica-v1.md`](docs/ml/evaluacion-clinica-v1.md).

---

## Arquitectura y datos

| Documento | Contenido |
|-----------|-----------|
| [`docs/architecture.md`](docs/architecture.md) | Decisiones de diseño |
| [`docs/database-architecture.md`](docs/database-architecture.md) | Esquema PostgreSQL |
| [`docs/diagramas.md`](docs/diagramas.md) | Diagramas Mermaid |
| [`docs/specs/BACKLOG.md`](docs/specs/BACKLOG.md) | Estado SDD |

---

## Desarrollo con IA

Proyecto desarrollado con **Cursor** (Vibe Coding). Prompts, errores y correcciones: [`docs/diario-ia/`](docs/diario-ia/).

Skills del repo: `@salle-sdd`, `@diario-ia`, `@salle-seguridad` (`.cursor/skills/`).

---

## Estado por fases (plan 1–10 mayo)

| Día | Entregable | Estado |
|-----|------------|--------|
| 1 | Infra Docker, Spark, Airflow, estructura | Hecho |
| 2 | Esquema BD, datos ejemplo, ingesta Spark, watcher | Hecho |
| 3 | Preprocesado RX (224×224, augmentation) | Hecho |
| 4 | Arquitectura ML, ResNet50 | Hecho |
| 5 | Entrenamiento v1, comparativa arquitecturas | Hecho |
| 6 | API Flask, pacientes, UI, integración ML | Hecho |
| 7 | Dashboard Streamlit, alertas, robustez API | Hecho |
| 8 | Monitorización, calidad, healthchecks | Hecho |
| 9 | Memoria, diagramas, ética, diario | Hecho |
| 10 | Presentación final | Pendiente |

---

## Persistencia Docker

| Volumen | Contenido |
|---------|-----------|
| `postgres_data` | Hospital + metadatos Airflow |
| `minio_data` | Radiografías |
| `airflow_metadata` | BD interna Airflow |
| `./data` | Raw, processed, flags watcher |

`docker compose down` sin `-v` conserva datos.

---

## Licencia

Proyecto académico — Máster / práctica integrada.
