# Spec-Driven Development (SDD)

Metodología obligatoria del encargo (`enunciado.md`): **especificar antes de codificar**.

Estructura del repo (dónde va cada módulo): [`../estructura-repositorio.md`](../estructura-repositorio.md).

## Flujo

1. Elegir tarea en [`BACKLOG.md`](BACKLOG.md)
2. Copiar [`_TEMPLATE.md`](_TEMPLATE.md) → `docs/specs/<modulo>-<nombre>.md`
3. Completar spec y criterios de aceptación
4. Implementar (la spec es el prompt base para Cursor)
5. Marcar tarea como `hecho` en el backlog
6. Registrar la sesión en el [Diario IA](../diario-ia/README.md)

## Skills de Cursor

| Skill | Uso |
|-------|-----|
| `@salle-sdd` | Contexto del proyecto, backlog, crear specs |
| `@diario-ia` | Guardar prompts y correcciones tras cada sesión |

Ubicación: `.cursor/skills/`
