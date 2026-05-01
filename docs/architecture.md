# Arquitectura — laSalle Health Center (salle-hospital)

## 1. Definición del sistema

**salle-hospital** es una plataforma de soporte hospitalario que integra Big Data, automatización y Deep Learning para el **laSalle Health Center**. El sistema cubre el encargo de la práctica: analizar datos clínicos y operativos, clasificar radiografías de tórax, automatizar procesos y visualizar resultados para apoyar decisiones médicas y operativas.

### Problema que resuelve

| Área | Necesidad del hospital | Solución propuesta |
|------|------------------------|-------------------|
| Datos dispersos | Historiales, logs e imágenes sin explotar | Pipeline unificado (ingesta → limpieza → transformación → análisis) |
| Diagnóstico por imagen | Clasificación manual lenta de radiografías | Modelo DL: **Sana / Neumonía / COVID-19** |
| Operaciones | Tareas repetitivas (informes, alertas) | Jobs Spark + API + reglas de automatización |
| Decisión | Falta de visibilidad agregada | Dashboard Streamlit + API REST |

### Alcance funcional (MVP)

1. **Ingesta**: CSV clínicos/operativos e imágenes RX hacia PostgreSQL y MinIO.
2. **Procesamiento**: jobs PySpark (validación, limpieza, agregados, features).
3. **IA**: inferencia y registro de predicciones sobre radiografías almacenadas en MinIO.
4. **API**: FastAPI como fachada (predicciones, pacientes, estado del pipeline, healthchecks).
5. **Dashboard**: Streamlit con métricas, matriz de confusión y alertas simuladas.
6. **Automatización**: procesamiento al detectar nuevos ficheros; alertas por calidad de datos o fallos.

---

## 2. Stack tecnológico

| Capa | Tecnología | Rol |
|------|------------|-----|
| API | **FastAPI** | REST, orquestación de servicios internos |
| IA | **TensorFlow** (Keras) | Clasificación triple de radiografías de tórax |
| Big Data | **Apache Spark** (PySpark) | Pipeline distribuible / escalable |
| BD relacional | **PostgreSQL** | Pacientes, metadatos, predicciones, logs de pipeline |
| Objetos | **MinIO** (S3-compatible) | Radiografías y artefactos no estructurados |
| Visualización | **Streamlit** | Dashboard clínico-operativo |
| Infra | **Docker + Docker Compose** | Despliegue reproducible |

**Elección TensorFlow** frente a PyTorch: API Keras estable para CNN y transfer learning (ResNet/EfficientNet vía `tf.keras.applications`), exportación **SavedModel** para el servicio `ml` en contenedor y ecosistema maduro de despliegue. Runtime en **Python 3.11** con TensorFlow 2.x.

---

## 3. Diagrama de arquitectura

```mermaid
flowchart TB
    subgraph Fuentes
        CSV[CSV clínicos / operativos]
        RX[Radiografías RX]
    end

    subgraph Ingesta
        WATCH[Watcher / ingest job]
    end

    subgraph Almacenamiento
        PG[(PostgreSQL)]
        MINIO[(MinIO — imágenes)]
    end

    subgraph Procesamiento
        SPARK[Apache Spark — PySpark]
    end

    subgraph Servicios
        API[FastAPI — API REST]
        ML[TensorFlow — servicio ML]
        DASH[Streamlit — Dashboard]
    end

    CSV --> WATCH
    RX --> WATCH
    WATCH --> PG
    WATCH --> MINIO
    PG --> SPARK
    MINIO --> SPARK
    SPARK --> PG
    MINIO --> ML
    ML --> PG
    API --> PG
    API --> MINIO
    API --> ML
    API --> SPARK
    DASH --> API
    DASH --> PG

    subgraph Usuarios
        MED[Médico / analista]
        OPS[Operaciones hospital]
    end

    MED --> DASH
    OPS --> DASH
    MED --> API
```

### Flujo de datos (resumen)

```
[Fuentes] → Ingesta → [PostgreSQL + MinIO]
                              ↓
                         Spark (ETL + calidad)
                              ↓
                    [PostgreSQL procesado]
                              ↓
              ML (inferencia RX) → API ← Dashboard
```

---

## 4. Componentes y responsabilidades

| Componente | Puerto (host) | Responsabilidad |
|------------|---------------|-----------------|
| `postgres` | 5432 | Datos estructurados, resultados, auditoría |
| `minio` | 9000 / 9001 | Bucket de radiografías (`xray-images`) |
| `spark-master` | 8080 (UI) | Coordinación del cluster Spark |
| `spark-worker` | — | Ejecución de jobs PySpark |
| `api` | 8000 | Endpoints REST, health, proxy a ML |
| `ml` | 8001 | Carga del modelo y predicción |
| `dashboard` | 8501 | Visualización e informes |
| `pipeline` | — | Jobs batch / programados (imagen Spark) |

---

## 5. Modelo de datos (borrador)

**PostgreSQL**

- `patients` — identificador, datos demográficos básicos (anonimizados/simulados).
- `studies` — estudio de imagen, ruta MinIO, timestamps.
- `predictions` — clase predicha, probabilidades, modelo, versión.
- `pipeline_runs` — job, estado, registros procesados, errores de calidad.

**MinIO**

- `xray-images/raw/` — imágenes entrantes.
- `xray-images/processed/` — preprocesadas para inferencia.

---

## 6. Automatizaciones previstas

- Vigilar carpeta/volumen de ingesta y lanzar job Spark.
- Validar esquema y completitud (registros incompletos, duplicados).
- Registrar alertas en PostgreSQL y mostrarlas en Streamlit.
- Generar informe resumen tras cada lote procesado.

---

## 7. Estructura de repositorio

```
salle-hospital/
├── api/              # FastAPI
├── dashboard/        # Streamlit
├── ml/               # TensorFlow (entrenamiento + inferencia)
├── pipeline/         # Jobs PySpark
├── data/             # Datos locales de desarrollo (no versionados en bloque)
├── docs/             # Arquitectura, especificaciones SDD
├── infra/            # Config Spark y utilidades
├── docker-compose.yml
└── README.md
```
