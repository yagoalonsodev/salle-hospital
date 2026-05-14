# Estructura del repositorio — salle-hospital

Documento **canónico** de carpetas y archivos. Debe coincidir con el árbol real del proyecto.

**Regla:** el resto de documentación no duplica árboles completos; enlaza aquí:

| Documento | Rol |
|-----------|-----|
| [`README.md`](../README.md) | Resumen raíz + arranque |
| [`docs/architecture.md`](architecture.md) | Arquitectura lógica (sin árbol duplicado) |
| [`docs/memoria-tecnica.md`](memoria-tecnica.md) | Memoria del proyecto |
| [`data/README.md`](../data/README.md) | Convenciones de datos |
| `api/`, `ml/`, `pipeline/`, `dashboard/`, `airflow/` README | Puntero al módulo |
| [`docs/specs/README.md`](specs/README.md) | SDD + ubicación de specs |
| [`AGENTS.md`](../AGENTS.md) | Guía Cursor |
| [`ml/README.md`](../ml/README.md) | Entrenamiento + inferencia |
| [`data/README.md`](../data/README.md) | Layout `data/raw` y `data/processed` |

Si cambia la estructura, actualizar **este archivo primero** y luego los enlaces anteriores.

---

## Vista general (raíz)

```
practica-tocha/                    # repo (producto: salle-hospital)
├── api/                           # API Flask + UI web hospitalaria
├── ml/                            # TensorFlow: entrenamiento + servicio inferencia
├── pipeline/                      # Jobs PySpark (ingesta, preprocesado)
├── dashboard/                     # Dashboard Streamlit (métricas / alertas)
├── scripts/                       # Utilidades compartidas (watcher, Airflow, calidad)
├── airflow/                       # DAGs y configuración Apache Airflow
├── infra/                         # SQL Postgres, Docker Spark, imagen watcher
├── data/                          # Datos locales (bind mount; mayoría en .gitignore)
├── docs/                          # Memoria, specs SDD, diario IA, diagramas
├── .cursor/skills/                # Skills Cursor (SDD, diario, seguridad)
├── docker-compose.yml             # Orquestación del stack completo
├── .env.example                   # Plantilla de variables (copiar a .env)
├── enunciado.md                   # Encargo de la práctica (local)
├── AGENTS.md                      # Guía rápida para agentes / Cursor
└── README.md                      # Arranque y enlaces principales
```

---

## `api/` — Capa hospitalaria (Flask)

```
api/
├── Dockerfile
├── requirements.txt
├── README.md
└── app/
    ├── __init__.py              # Factory Flask, registro blueprints
    ├── config.py                # Settings desde entorno
    ├── db.py                    # Pool PostgreSQL
    ├── logging_config.py        # Logging centralizado (Día 8)
    ├── validators.py            # Validación upload RX
    ├── validators_patients.py   # Validación pacientes
    ├── wsgi.py                  # Entrada Gunicorn
    ├── routes/                  # HTTP (blueprints)
    │   ├── web.py               # UI HTML (/)
    │   ├── health.py            # GET /health
    │   ├── metrics.py           # GET /metrics
    │   ├── upload.py            # POST /upload
    │   ├── predict.py           # POST /predict
    │   ├── patients.py          # CRUD /api/patients
    │   ├── sites.py             # GET /api/sites
    │   ├── studies.py           # Estudios e imágenes
    │   └── dashboard.py         # GET /api/dashboard (Streamlit)
    ├── services/                # Lógica de negocio
    │   ├── ml_client.py         # Cliente HTTP → servicio ml
    │   ├── minio_store.py       # MinIO (upload/download)
    │   ├── pipeline.py          # Orquestación upload + inferencia
    │   └── retry_util.py        # Reintentos (Día 8)
    ├── repositories/            # Acceso a datos
    │   ├── patients.py
    │   ├── sites.py
    │   ├── dashboard.py
    │   └── alerts.py
    ├── templates/               # Jinja2 (index.html, …)
    └── static/
        ├── css/
        └── js/                  # app.js, patients.js, …
```

---

## `ml/` — Inteligencia artificial

```
ml/
├── Dockerfile                   # Servicio inferencia (FastAPI + TensorFlow)
├── requirements.txt
├── app/                         # Servicio en runtime (puerto 8001)
│   ├── main.py                  # FastAPI /health, /predict
│   ├── inference.py             # Carga modelo, predicción PIL
│   └── logging_config.py
├── scripts/                     # Entrenamiento offline (no en contenedor API)
│   ├── training_core.py
│   ├── train_resnet50.py
│   ├── train_compare_architectures.py
│   └── …
├── notebooks/
│   └── 01_exploracion_arquitectura.ipynb
└── models/                      # Artefactos ( .h5 en .gitignore salvo reports)
    ├── architectures.py
    ├── rx_resnet50_v1.h5        # Modelo producción (local)
    ├── reports/                 # Métricas, matrices, JSON comparativa
    ├── checkpoints/             # Checkpoints entrenamiento (gitignore)
    └── savedmodel/              # Export SavedModel (gitignore)
```

---

## `pipeline/` — Big Data (PySpark)

```
pipeline/
├── Dockerfile                   # Imagen salle-pipeline (spark-submit)
├── requirements.txt
├── README.md
└── jobs/
    ├── ingest_validate_images.py   # Ingesta, calidad, MinIO
    ├── ingest_csv_to_postgres.py   # CSV clínico → patients/studies
    ├── preprocess_images.py        # 224×224, augmentation, splits
    ├── image_transforms.py         # Transformaciones Pillow
    └── db_log.py                     # pipeline_runs, alertas, calidad BD
```

---

## `dashboard/` — Visualización (Streamlit)

```
dashboard/
├── Dockerfile
├── requirements.txt
├── README.md
└── app/
    ├── main.py                  # Pestañas IA / pipeline / alertas
    └── api_client.py            # Cliente → GET /api/dashboard
```

---

## `scripts/` — Utilidades transversales

Montado en contenedores `pipeline`, `airflow` y `watcher` como `/opt/scripts`.

```
scripts/
├── image_watcher.py             # Vigila incoming/ → raw/
├── watcher_state.py             # pending.flag, events
├── build_clinical_data.py         # manifest + studies.csv
├── airflow_trigger_ingest.py      # spark-submit vía Docker API
├── airflow_callbacks.py           # on_failure → alertas
├── data_quality_audit.py          # Auditoría registros incompletos
├── db_alerts.py                   # INSERT en tabla alerts
├── salle_logging.py               # Logging unificado
├── env_utils.py                   # MinIO desde entorno
├── verify_pipeline_integration.py
└── convert_rx_to_jpeg.py
```

---

## `airflow/` — Orquestación

```
airflow/
├── README.md
├── dags/
│   └── salle_rx_pipeline.py     # Watcher → manifest → Spark → auditoría
├── config/
│   └── log_config.py            # Logging Airflow
├── plugins/                     # Extensiones (vacío / .gitkeep)
└── logs/                        # Logs de tareas (gitignore, .gitkeep)
```

---

## `infra/` — Infraestructura

```
infra/
├── postgres/
│   ├── 01-init-salle-schema.sql
│   ├── init-airflow-db.sql
│   └── 03-…05-*.sql             # Migraciones incrementales
├── spark/
│   └── Dockerfile               # Spark 3.5 + Pillow en workers
└── watcher/
    └── Dockerfile               # Imagen salle-watcher
```

---

## `data/` — Datos locales (volumen Docker)

No se versionan los binarios masivos; solo `.gitkeep` y algunos metadatos (ver `.gitignore`).

```
data/
├── raw/
│   ├── .gitkeep
│   ├── clinical/                # studies.csv, pipeline_events.csv
│   └── covid19_vs_pneumonia/
│       ├── manifest.csv
│       ├── incoming/            # Bandeja watcher (train|test/CLASE/*.jpg)
│       ├── train/{NORMAL,PNEUMONIA,COVID19}/
│       └── test/{NORMAL,PNEUMONIA,COVID19}/
└── processed/
    ├── .gitkeep
    ├── manifest/                # validated.parquet, rejected, ingest_report.json
    ├── features/v1/             # Imágenes 224×224 por split/label
    └── watcher/                 # pending.flag, events.jsonl
```

---

## `docs/` — Documentación

```
docs/
├── architecture.md              # Decisiones de arquitectura
├── database-architecture.md     # Esquema PostgreSQL
├── diagramas.md                 # Diagramas Mermaid
├── memoria-tecnica.md           # Memoria del proyecto
├── etica.md                     # Ética + prompt injection
├── estructura-repositorio.md    # ← este archivo
├── preprocess-distributed-justification.md
├── ml/
│   ├── arquitectura-rx.md
│   ├── resultados-entrenamiento-v1.md
│   └── evaluacion-clinica-v1.md
├── specs/                       # SDD: specs por módulo + BACKLOG.md
│   ├── README.md
│   ├── BACKLOG.md
│   ├── _TEMPLATE.md
│   └── *.md
└── diario-ia/
    ├── README.md
    ├── INDEX.md
    └── entradas/YYYY-MM-DD.md
```

---

## `.cursor/skills/` — Desarrollo asistido (Cursor)

```
.cursor/skills/
├── salle-sdd/                   # Spec-driven development + backlog
├── diario-ia/                   # Diario de prompts y correcciones
└── salle-seguridad/             # Revisión secretos antes de commit
```

---

## Qué no va en el repositorio

| Elemento | Motivo |
|----------|--------|
| `.env` | Secretos locales |
| `data/raw/**/*.jpg` | Volumen (~6k imágenes) |
| `ml/models/*.h5` | Artefactos pesados |
| `airflow/logs/*` | Logs de ejecución |
| `ml/.venv-metal/` | Entorno virtual local |
| `__pycache__/` | Bytecode Python |

---

## Mapa rápido: carpeta → responsabilidad

| Carpeta | Rol en el sistema |
|---------|-------------------|
| `api/` | UI clínica + REST + integración ML/MinIO/BD |
| `ml/app/` | Inferencia TensorFlow |
| `ml/scripts/` | Entrenamiento y exportación |
| `pipeline/jobs/` | ETL Spark |
| `scripts/` | Watcher, triggers Airflow, alertas |
| `airflow/dags/` | Automatización programada |
| `dashboard/` | Cuadro de mando analítico |
| `infra/postgres/` | DDL y migraciones |
| `data/` | Almacenamiento bind-mount |
| `docs/specs/` | Contratos SDD antes de codificar |

---

*Última revisión: alineado con el árbol del repo tras Días 1–9 (mayo 2026).*
