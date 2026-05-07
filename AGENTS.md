# Agentes y skills — salle-hospital

Guía para Cursor en este repositorio (práctica laSalle Health Center).

## Skills del proyecto

| Skill | Invocación | Función |
|-------|------------|---------|
| Diario IA | `@diario-ia` | Tras cada tarea, **preguntar** si guardar prompt/respuesta/corrección en `docs/diario-ia/` |
| SDD + backlog | `@salle-sdd` | Leer proyecto, specs antes de código, mantener `docs/specs/BACKLOG.md` |

Ruta: `.cursor/skills/`

## Reglas de trabajo

1. **SDD:** No implementar módulos nuevos sin spec en `docs/specs/` (copiar `_TEMPLATE.md`).
2. **Contexto:** Leer `enunciado.md`, `docs/architecture.md` y `BACKLOG.md` antes de planificar.
3. **Diario:** Al cerrar una sesión sustantiva, ofrecer guardar en el diario (confirmación del usuario).
4. **Backlog:** Actualizar estados en `docs/specs/BACKLOG.md` al completar tareas.

## Documentación clave

- Encargo: `enunciado.md`
- Arquitectura: `docs/architecture.md`
- Specs y tareas: `docs/specs/`
- Diario IA: `docs/diario-ia/`

## Estado rápido (2026-05-07)

- **Hecho:** Días 1–7 — infra, pipeline, ML, API Flask + UI, dashboard Streamlit.
- **Siguiente:** D8 — DAGs ETL/ML batch; D9 — memoria, ética, presentación.
