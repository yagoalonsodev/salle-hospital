# Arquitectura de base de datos — salle_hospital

PostgreSQL 16 aloja los datos **estructurados** de la aplicación. Las radiografías (no estructuradas) viven en **MinIO**; PostgreSQL guarda metadatos, predicciones, trazas del pipeline y alertas.

## Instancias lógicas

| Base de datos | Uso | Creación |
|---------------|-----|----------|
| `salle_hospital` | App: pacientes, estudios, ML, pipeline | `POSTGRES_DB` + `01-init-salle-schema.sql` |
| `airflow` | Metadatos Airflow | `02-init-airflow-db.sql` |

Conexión app (Docker):  
`postgresql://salle:salle_secret@postgres:5432/salle_hospital`

## Diagrama entidad-relación

```mermaid
erDiagram
    patients ||--o{ studies : has
    studies ||--o{ predictions : receives
    pipeline_runs ||--o{ pipeline_events : logs
    pipeline_runs ||--o{ data_quality_issues : finds
    pipeline_runs ||--o{ alerts : raises
    studies ||--o{ data_quality_issues : affects

    patients {
        varchar patient_id PK
        char sex
        varchar age_range
        varchar site_code
        timestamptz created_at
    }

    studies {
        varchar study_id PK
        varchar patient_id FK
        text file_path UK
        text minio_object_key
        enum split
        enum label
        varchar source_dataset
        timestamptz captured_at
    }

    predictions {
        bigint prediction_id PK
        varchar study_id FK
        enum predicted_label
        numeric prob_sana
        numeric prob_neumonia
        numeric prob_covid
        varchar model_name
        varchar model_version
    }

    pipeline_runs {
        varchar run_id PK
        varchar job_name
        enum status
        int records_in
        int records_out
    }

    pipeline_events {
        varchar event_id PK
        varchar run_id FK
        varchar stage
        enum status
    }

    data_quality_issues {
        bigint issue_id PK
        enum issue_type
        varchar study_id FK
    }

    alerts {
        bigint alert_id PK
        enum severity
        boolean acknowledged
    }
```

## Tablas y responsabilidad

| Tabla | Rol | Origen de datos |
|-------|-----|-----------------|
| `patients` | Paciente anonimizado | CSV `data/raw/clinical/patients.csv` → ingesta Spark |
| `studies` | Metadatos de cada RX + enlace a fichero/MinIO | CSV `studies.csv` + `manifest.csv` |
| `predictions` | Resultado inferencia TensorFlow | Servicio `ml` tras cargar estudio |
| `pipeline_runs` | Cabecera de job (ingesta, ETL, ML batch) | Airflow / Spark |
| `pipeline_events` | Log por etapa dentro de un run | CSV eventos / jobs |
| `data_quality_issues` | Duplicados, incompletos, corruptos | Job PySpark calidad (D2-05) |
| `alerts` | Avisos en dashboard | Reglas post-ETL / fallos DAG |

## Tipos enumerados

| ENUM | Valores | Uso |
|------|---------|-----|
| `study_label` | `sana`, `neumonia`, `covid` | Ground truth y predicción (enunciado 3 clases) |
| `data_split` | `train`, `val`, `test` | Partición ML |
| `pipeline_status` | `pending`, `running`, `ok`, `failed` | Jobs |
| `alert_severity` | `info`, `warning`, `critical` | Dashboard |
| `quality_issue_type` | `incomplete`, `duplicate`, `corrupt`, … | Calidad de datos |

## Relación con MinIO

```
Estudio (PostgreSQL)          Imagen (MinIO)
─────────────────────         ─────────────────────────────
study_id                  →   xray-images/raw/{study_id}.jpg
minio_object_key (nullable)   (relleno tras D2-04)
file_path                     ruta local en ingesta inicial
```

Flujo previsto:

1. Ingesta: CSV → `patients`, `studies` (sin `minio_object_key`).
2. Carga imágenes: fichero → MinIO → `UPDATE studies SET minio_object_key = …`.
3. Inferencia: ML lee MinIO, escribe `predictions`.

## Vistas

| Vista | Propósito |
|-------|-----------|
| `v_study_counts_by_label` | Conteos por clase y split (dashboard) |
| `v_prediction_summary` | Agregados de probabilidades por clase predicha |

## Scripts SQL

| Archivo | Cuándo se ejecuta |
|---------|-------------------|
| `infra/postgres/01-init-salle-schema.sql` | Primer arranque del volumen Postgres |
| `infra/postgres/02-init-airflow-db.sql` | Idem (usuario/BD Airflow) |

**Importante:** los scripts de `docker-entrypoint-initdb.d` solo corren si el volumen es nuevo. Si ya levantaste Postgres antes:

```bash
docker compose down -v   # borra volumen — pierdes datos locales
docker compose up -d
```

Para aplicar el esquema sin borrar volumen (desarrollo):

```bash
docker exec -i salle-postgres psql -U salle -d salle_hospital < infra/postgres/01-init-salle-schema.sql
```

## Mapeo CSV → tablas

| CSV | Tabla |
|-----|-------|
| `patients.csv` | `patients` |
| `studies.csv` | `studies` |
| `pipeline_events.csv` | `pipeline_events` (+ fila previa en `pipeline_runs`) |

El script de ingesta (D2-03) debe crear `pipeline_runs` antes de insertar eventos por la FK.

## Índices

Índices en FKs (`patient_id`, `study_id`, `run_id`), filtros de dashboard (`label`, `severity`, `acknowledged`) y orden temporal (`ingested_at`, `inferred_at`).

## Seguridad y ética (simulado)

- Sin nombres, DNI ni contacto; solo `patient_id` opaco.
- Credenciales en `.env` (no versionar).
- En memoria: limitaciones del etiquetado débil y sesgo de clases.

## Referencias

- Spec SDD: [`docs/specs/pipeline-esquema-db.md`](specs/pipeline-esquema-db.md)
- Modelo general: [`architecture.md`](architecture.md)
- Datos raw: [`../data/README.md`](../data/README.md)
