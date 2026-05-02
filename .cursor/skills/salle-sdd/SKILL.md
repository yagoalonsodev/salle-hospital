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

## Ejemplo de sesión SDD

| Sesión | Tema |
|--------|------|
| [2026-05-16-esquema-db.md](sessions/2026-05-16-esquema-db.md) | Spec → SQL → doc BD |
| [2026-05-16-sin-patients-csv.md](sessions/2026-05-16-sin-patients-csv.md) | Quitar `patients.csv`; solo `studies` + manifest |
