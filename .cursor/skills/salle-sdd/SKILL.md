---
name: salle-sdd
description: >-
  Spec-Driven Development para salle-hospital (práctica laSalle). Lee el proyecto
  (enunciado, arquitectura, backlog), redacta specs antes de codificar, y mantiene
  tareas hechas y pendientes en docs/specs/BACKLOG.md. Usar al planificar módulos,
  implementar features, preguntar qué falta, o cuando el usuario pida SDD, spec,
  backlog o estado del proyecto.
---

# SDD + contexto del proyecto — salle-hospital

## Principio SDD (enunciado)

**Antes de escribir código** (o pedir generación masiva a la IA), redactar una spec en `docs/specs/`. La spec es el **prompt base** estructurado.

## Seguridad (obligatorio)

Antes de cada commit, aplicar skill **`salle-seguridad`** (`.cursor/skills/salle-seguridad/SKILL.md`):

- Sin secretos en código Python (usar `.env` + `scripts/env_utils.py`).
- No commitear `.env` ni trailers `Co-authored-by: Cursor` en mensajes.

## Lectura obligatoria del contexto

Antes de planificar o implementar, lee en este orden:

1. `enunciado.md` — requisitos y entregables
2. `docs/architecture.md` — stack y diagramas
3. `docs/specs/BACKLOG.md` — hecho / en curso / pendiente
4. `README.md` — arranque y estado por días
5. `docker-compose.yml` — servicios existentes
6. Código del módulo afectado (`api/`, `ml/`, `pipeline/`, `dashboard/`, `airflow/dags/`)

No improvises arquitectura que contradiga estos documentos.

## Flujo SDD por componente

```
1. BACKLOG.md → elegir ítem pendiente
2. Crear docs/specs/<modulo>-<feature>.md desde _TEMPLATE.md
3. Revisar spec con el usuario (si pide)
4. Implementar
5. Marcar ítem en BACKLOG.md como hecho
6. Skill diario-ia → ofrecer guardar la sesión
```

## Plantilla de spec

Usar [spec-template.md](spec-template.md) o copiar desde `docs/specs/_TEMPLATE.md`.

Campos mínimos del enunciado:

- Descripción funcional
- Inputs / outputs
- Restricciones técnicas y de negocio
- Criterios de aceptación

## BACKLOG.md

- **Fuente de verdad** de progreso del proyecto.
- Actualizar en cada sesión de implementación.
- Estados: `pendiente` | `en curso` | `hecho` | `bloqueado`
- Enlazar cada ítem grande a su spec cuando exista.

## Convención de nombres de specs

`docs/specs/<capa>-<nombre-corto>.md`

Ejemplos: `pipeline-ingesta-csv.md`, `ml-clasificacion-rx.md`, `api-predict-endpoint.md`

## DAGs y automatización

Specs de Airflow en `docs/specs/airflow-*.md`; implementación en `airflow/dags/`.

## Preguntas frecuentes del usuario

| Pregunta | Acción |
|----------|--------|
| ¿Qué falta por hacer? | Leer `BACKLOG.md` sección Pendiente |
| ¿Qué llevamos hecho? | Leer `BACKLOG.md` sección Hecho |
| ¿Siguiente paso? | Primer `pendiente` de mayor prioridad según plan 1–10 mayo |
| ¿Cómo documento la IA? | Activar skill `diario-ia` |

## Integración con Diario IA

Toda implementación relevante debería tener entrada en el diario (con confirmación del usuario). Enlazar spec ↔ entrada del diario.

## Documentación de referencia del repo

| Tema | Ruta |
|------|------|
| Encargo | `enunciado.md` |
| Arquitectura sistema | `docs/architecture.md` |
| Arquitectura BD | `docs/database-architecture.md` |
| Backlog | `docs/specs/BACKLOG.md` |
| Plantilla spec | `docs/specs/_TEMPLATE.md` |
| Datos raw | `data/README.md` |

## Convención de nombres en `sessions/`

El prefijo `YYYY-MM-DD` debe coincidir con la **fecha del commit** en `main` (`git log --format=%ad`). Varios commits el mismo día → mismo prefijo, distinto sufijo. Trabajo sin commit → `pendiente-*.md` hasta commitear.

## Sesiones (alineadas con commits)

| Sesión | Commit | Tema |
|--------|--------|------|
| [2026-05-01-skills-diario.md](sessions/2026-05-01-skills-diario.md) | `7fe54ab` 21:20 | Skills Diario IA + SDD |
| [2026-05-02-datos-ejemplo.md](sessions/2026-05-02-datos-ejemplo.md) | `fda8c86` 09:00 | Datos raw, CSV, manifest |
| [2026-05-02-esquema-db.md](sessions/2026-05-02-esquema-db.md) | `fda8c86` 09:00 | Esquema PostgreSQL |
| [2026-05-02-sin-patients-csv.md](sessions/2026-05-02-sin-patients-csv.md) | `77607d0` 10:00 | Sin `patients.csv` |
| [2026-05-02-ingesta-imagenes.md](sessions/2026-05-02-ingesta-imagenes.md) | `33c9140` 11:00 | PySpark ingesta, validación, dedup, MinIO |
| [2026-05-02-verificacion-integracion.md](sessions/2026-05-02-verificacion-integracion.md) | `b215ee3` 11:30 | Verificación E2E Postgres + MinIO |
| [2026-05-02-watcher-airflow.md](sessions/2026-05-02-watcher-airflow.md) | `9848819` 14:00 | Watcher RX, DAG Airflow, logging, volúmenes |
| [2026-05-03-preprocesado-imagenes.md](sessions/2026-05-03-preprocesado-imagenes.md) | `4becbc8`–`9c49bd3` | Resize, aug, split train/val/test (PySpark) |
| [2026-05-04-arquitectura-ml.md](sessions/2026-05-04-arquitectura-ml.md) | `c95ce67` | Elección ResNet50, notebook exploratorio |
| [2026-05-05-informe-arquitecturas.md](sessions/2026-05-05-informe-arquitecturas.md) | `d3b3312` 16:30 | Comparativa 4 CNN, F1 macro, conclusión memoria |

## Día 5 — Entrenamiento y comparativa ML

| Recurso | Ruta |
|---------|------|
| Spec | `docs/specs/ml-entrenamiento.md` |
| Informe | `ml/notebooks/01_exploracion_arquitectura.ipynb` |
| Comparativa | `ml/models/reports/architecture_comparison.json` |
| Core | `ml/scripts/training_core.py` |

## Día 3 — Preprocesado ML (`features/v1/`)

| Recurso | Ruta |
|---------|------|
| Spec | `docs/specs/pipeline-preprocesado-imagenes.md` |
| Justificación Spark | `docs/preprocess-distributed-justification.md` |
| Transforms | `pipeline/jobs/image_transforms.py` |
| Job | `pipeline/jobs/preprocess_images.py` |
| Workers PIL | `infra/spark/Dockerfile` |

```bash
docker compose build spark-master pipeline
docker exec salle-pipeline /opt/spark/bin/spark-submit \
  --master spark://spark-master:7077 --driver-memory 2g \
  /opt/pipeline/jobs/preprocess_images.py
```

Salida: `data/processed/features/v1/` + `preprocess_report.json` (6399 → ~19k muestras con aug en train).

## Automatización (watcher + Airflow)

| Recurso | Ruta |
|---------|------|
| Spec | `docs/specs/airflow-automatizacion-watcher.md` |
| Watcher | `scripts/image_watcher.py`, servicio `salle-watcher` |
| DAG | `airflow/dags/salle_rx_pipeline.py` |
| Trigger Spark | `scripts/airflow_trigger_ingest.py` |
| Logging | `airflow/config/log_config.py` |
| Guía | `airflow/README.md` |
| Bandeja RX | `data/raw/covid19_vs_pneumonia/incoming/` |

**MinIO:** `MAX_UPLOAD=0` en `docker-compose.yml` (Airflow + pipeline) — sube **todas** las imágenes válidas, sin tope.

Tras cambios: `docker compose up -d watcher airflow`, `airflow dags unpause salle_rx_pipeline`, copiar RX a `incoming/`.

## Verificación tras cambios de pipeline

Tras implementar o modificar jobs en `pipeline/jobs/`:

1. Levantar stack: `docker compose up -d`
2. Aplicar esquema si hace falta: `infra/postgres/01-init-salle-schema.sql`
3. Normalizar JPEG si hace falta: `scripts/convert_rx_to_jpeg.py`
4. Ejecutar job (ver `pipeline/README.md`)
5. Ejecutar `scripts/verify_pipeline_integration.py` dentro de `salle-pipeline`
6. Si hay watcher/DAG: `docker logs salle-watcher`; `airflow dags trigger salle_rx_pipeline`
