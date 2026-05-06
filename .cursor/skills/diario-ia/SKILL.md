---
name: diario-ia
description: >-
  Gestiona el Diario de desarrollo con IA (entregable obligatorio de la práctica).
  Tras cada interacción sustantiva, pregunta si guardar prompt, respuesta y correcciones
  en docs/diario-ia/. Usar cuando el usuario mencione diario IA, vibe coding, prompts,
  documentar IA, o al cerrar tareas de desarrollo con asistencia de Cursor.
---

# Diario IA — laSalle Health Center

## Seguridad (obligatorio)

- **No** pegar contraseñas, tokens ni contenido de `.env` en entradas del diario.
- Revisar skill **`salle-seguridad`** antes de guardar entradas que mencionen configuración o despliegue.

## Objetivo

Documentar el uso de IA (Cursor) según `enunciado.md`: prompts, resultados, correcciones e iteraciones. Es un **entregable obligatorio** de la memoria técnica.

## API REST — un solo framework (recordatorio)

Al documentar el Día 6 o cambios en la API:

| Qué | Framework | Dónde |
|-----|-----------|-------|
| API REST + UI web | **Flask** (único) | `api/` |
| Inferencia TensorFlow | FastAPI (microservicio) | `ml/` — no sustituye a la API Flask |

En el diario, no describir «API en FastAPI y Flask» a la vez: la fachada del hospital es **solo Flask** (`salle-api`, puerto 8000). FastAPI aparece solo en el servicio `ml` interno.

## Cuándo activar el flujo

Al terminar una respuesta **sustantiva** (código, infra, diseño, debugging, specs), **antes de cerrar**:

1. Usa **AskQuestion** (si está disponible) con:

   - **Pregunta:** `¿Quieres guardar esta interacción en el Diario IA?`
   - **Opciones:**
     - `Sí, guardar`
     - `No, ahora no`
     - `Sí, pero quiero editar antes`

2. Si AskQuestion no está disponible, pregunta lo mismo en texto al final del mensaje.

3. **No guardes sin confirmación explícita** del usuario (salvo que diga «guárdalo en el diario» en el mismo mensaje).

## Dónde guardar

| Recurso | Ruta |
|---------|------|
| Entradas del día | `docs/diario-ia/entradas/YYYY-MM-DD.md` |
| Plantilla de entrada | [entry-template.md](entry-template.md) |
| Índice global | `docs/diario-ia/INDEX.md` |

- Un archivo por **día** (`YYYY-MM-DD.md`); varias entradas separadas por `---`.
- ID de entrada: `### Entrada NNN — título corto` (NNN = 001, 002… por día).
- Tras guardar, actualiza `docs/diario-ia/INDEX.md` (fecha, título, enlace al ancla).

## Contenido mínimo de cada entrada

Copia la plantilla de [entry-template.md](entry-template.md). Campos obligatorios:

- **Herramienta:** Cursor (modelo si se conoce)
- **Prompt del usuario** (texto literal o resumen fiel)
- **Respuesta de la IA** (resumen de lo hecho, no pegar todo el chat)
- **Resultado:** `acierto` | `parcial` | `corrección`
- **Corrección** (si aplica): qué estaba mal, prompt de corrección, solución final
- **Archivos afectados** (rutas)
- **Spec SDD** (si existe): enlace a `docs/specs/…`
- **Reflexión** (1–3 frases): qué aportó la IA, limitaciones

## Si el usuario elige «editar antes»

Muestra el borrador en markdown y pide cambios. Solo escribe el archivo cuando confirme.

## Entrada inicial de ejemplo

Ver `docs/diario-ia/entradas/2026-05-01.md` como referencia de formato.

## Índice y sesiones

| Recurso | Ruta |
|---------|------|
| Índice global | `docs/diario-ia/INDEX.md` |
| Entradas por día | `docs/diario-ia/entradas/YYYY-MM-DD.md` |
| Plantilla | [entry-template.md](entry-template.md) |
| Convención | Prefijo `YYYY-MM-DD` = fecha del commit (`git log`); sin commit → `pendiente-*.md` |
| 2026-05-01 | [sessions/2026-05-01-skills-diario.md](sessions/2026-05-01-skills-diario.md) (`7fe54ab`) |
| 2026-05-02 datos | [sessions/2026-05-02-datos-ejemplo.md](sessions/2026-05-02-datos-ejemplo.md) (`fda8c86`) |
| 2026-05-02 BD | [sessions/2026-05-02-esquema-db.md](sessions/2026-05-02-esquema-db.md) (`fda8c86`) |
| 2026-05-02 CSV | [sessions/2026-05-02-sin-patients-csv.md](sessions/2026-05-02-sin-patients-csv.md) (`77607d0`) |
| 2026-05-02 pipeline | [sessions/2026-05-02-ingesta-imagenes.md](sessions/2026-05-02-ingesta-imagenes.md) |
| 2026-05-02 verificación | [sessions/2026-05-02-verificacion-integracion.md](sessions/2026-05-02-verificacion-integracion.md) |
| 2026-05-02 automatización | [sessions/2026-05-02-watcher-airflow.md](sessions/2026-05-02-watcher-airflow.md) |
| 2026-05-03 preprocesado | [sessions/2026-05-03-preprocesado-imagenes.md](sessions/2026-05-03-preprocesado-imagenes.md) |
| 2026-05-04 arquitectura ML | `docs/diario-ia/entradas/2026-05-04.md` (`c95ce67`) |
| 2026-05-05 informe arquitecturas | [entradas/2026-05-05.md](../../docs/diario-ia/entradas/2026-05-05.md) (`d3b3312`) |
| 2026-05-06 API Flask + UI | [entradas/2026-05-06.md](../../docs/diario-ia/entradas/2026-05-06.md) (commit Día 6) |

## Día 5 — Informe comparativa arquitecturas

| Recurso | Ruta |
|---------|------|
| Entrada canónica | `docs/diario-ia/entradas/2026-05-05.md` |
| Spec | `docs/specs/ml-entrenamiento.md` |
| Notebook | `ml/notebooks/01_exploracion_arquitectura.ipynb` |

Documentar: 4 arquitecturas, F1 macro, FN neumonía→sana, DenseNet vs ResNet50, EfficientNet fallido.

## Día 6 — API Flask + integración IA (hecho)

| Recurso | Ruta |
|---------|------|
| Specs | `docs/specs/api-predict.md`, `docs/specs/api-pacientes.md` |
| Entrada canónica | [entradas/2026-05-06.md](../../docs/diario-ia/entradas/2026-05-06.md) |
| Sesión SDD | [sessions/2026-05-06-api-flask-ui.md](../salle-sdd/sessions/2026-05-06-api-flask-ui.md) |
| API | `api/README.md` |

Documentar: Flask único en `api/`, CRUD pacientes, `display_name`, tabla `sites`, subida → MinIO → ML → `predictions`, UI 3 pestañas (galería + resumen con `study_id`), sin placeholders en BD.

## Día 3 — Preprocesado para entrenamiento

| Recurso | Ruta |
|---------|------|
| Entrada canónica | `docs/diario-ia/entradas/2026-05-03.md` |
| Spec | `docs/specs/pipeline-preprocesado-imagenes.md` |

Documentar: resize 224, augmentation train, split train/val/test, justificación PySpark, resultado `preprocess_report.json`.

## Automatización (watcher + Airflow)

| Recurso | Ruta |
|---------|------|
| Spec SDD | `docs/specs/airflow-automatizacion-watcher.md` |
| Watcher | `scripts/image_watcher.py`, contenedor `salle-watcher` |
| DAG | `airflow/dags/salle_rx_pipeline.py` |
| Guía | `airflow/README.md` |

**MinIO:** `MAX_UPLOAD=0` — ingesta completa a MinIO (todas las válidas). No usar límites de prueba en entregables.

Al documentar en diario: prompt, prueba con imagen en `incoming/`, resultado del DAG y `verify_pipeline_integration.py`.

## Tras verificar pipeline / infra

Si el usuario pide comprobar que «funciona todo» (MinIO, Postgres, encargo):

1. Ejecutar o revisar salida de `ingest_validate_images.py`
2. Correr `scripts/verify_pipeline_integration.py` en `salle-pipeline`
3. Documentar resultado en entrada de diario (`acierto` / `corrección`)
4. Actualizar sesión en `.cursor/skills/diario-ia/sessions/` si hubo cambios relevantes

## Relación con SDD

Si la interacción implementó una spec, enlaza `docs/specs/<nombre>.md` y actualiza el estado en `docs/specs/BACKLOG.md` (skill `salle-sdd`).
