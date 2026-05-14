# Diagramas — laSalle Health Center

Diagramas en Mermaid para memoria y presentación. Renderizan en GitHub, VS Code y muchas herramientas de exportación a PDF.

**Estructura de carpetas del código:** [`estructura-repositorio.md`](estructura-repositorio.md) (no confundir con estos diagramas lógicos/de despliegue).

---

## 1. Arquitectura lógica

```mermaid
flowchart TB
    subgraph Fuentes
        CSV[CSV clínico]
        RX[Radiografías JPG]
        INC[incoming/ watcher]
    end

    subgraph Orquestación
        AF[Apache Airflow<br/>salle_rx_pipeline]
    end

    subgraph Almacenamiento
        PG[(PostgreSQL)]
        S3[(MinIO)]
    end

    subgraph Procesamiento
        SP[Apache Spark<br/>PySpark]
    end

    subgraph Servicios
        API[Flask API :8000]
        ML[TensorFlow ML :8001]
        DASH[Streamlit :8501]
    end

    INC --> W[Watcher]
    RX --> W
    W --> SP
    CSV --> SP
    AF --> SP
    AF --> PG
    SP --> PG
    SP --> S3
    S3 --> ML
    ML --> PG
    API --> PG
    API --> S3
    API --> ML
    DASH --> API
```

---

## 2. Flujo de una radiografía clínica (API)

```mermaid
sequenceDiagram
    participant U as Usuario web
    participant API as Flask API
    participant M as MinIO
    participant DB as PostgreSQL
    participant ML as Servicio ML

    U->>API: POST /upload (JPG + patient_id)
    API->>API: Validar tamaño/MIME
    API->>M: put_object (retry x3)
    API->>DB: INSERT study
    API->>ML: POST /predict (bytes o key)
    ML-->>API: clase + probabilidades
    API->>DB: INSERT prediction
    API-->>U: study_id + resultado
```

---

## 3. Automatización watcher + Airflow

```mermaid
flowchart LR
    A[JPG en incoming/] --> B[Watcher mueve a raw/]
    B --> C[pending.flag]
    C --> D{DAG cada 15 min}
    D -->|sin flag| E[Short-circuit OK]
    D -->|con flag| F[rebuild_manifest]
    F --> G[spark_ingest_images]
    G --> H[clear_pending_flag]
    H --> I[data_quality_audit]
    G --> PG[(PostgreSQL)]
    G --> S3[(MinIO)]
```

---

## 4. Modelo de datos (simplificado)

```mermaid
erDiagram
    patients ||--o{ studies : tiene
    studies ||--o| predictions : genera
    pipeline_runs ||--o{ pipeline_events : registra
    pipeline_runs ||--o{ data_quality_issues : detecta
    pipeline_runs ||--o{ alerts : dispara

    patients {
        uuid patient_id PK
        string display_name
        string age_range
        uuid site_id FK
    }
    studies {
        uuid study_id PK
        uuid patient_id FK
        string minio_object_key
        string label
    }
    predictions {
        uuid prediction_id PK
        uuid study_id FK
        string predicted_class
        float confidence
    }
```

---

## 5. Despliegue Docker Compose

```mermaid
flowchart TB
    subgraph Host["localhost"]
        P8000[API :8000]
        P8001[ML :8001]
        P8501[Dashboard :8501]
        P8081[Airflow :8081]
        P5432[Postgres :5432]
        P9000[MinIO :9000]
        P8080[Spark UI :8080]
    end

    subgraph Containers
        api
        ml
        dashboard
        airflow
        postgres
        minio
        spark-master
        spark-worker
        pipeline
        watcher
    end

    P8000 --- api
    P8001 --- ml
    P8501 --- dashboard
    P8081 --- airflow
```

---

## 6. Capas de la API Flask (SDD)

```mermaid
flowchart TB
    R[routes/] --> S[services/]
    S --> REPO[repositories/]
    REPO --> DB[(PostgreSQL)]
    S --> MINIO[(MinIO)]
    S --> MLsvc[Servicio ML HTTP]
    T[templates/ + static/js/] --> R
```
