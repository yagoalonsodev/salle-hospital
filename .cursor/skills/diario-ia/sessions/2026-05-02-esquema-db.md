# Diario IA — Esquema PostgreSQL (2026-05-02)

> Copia orientativa; entrada canónica en `docs/diario-ia/entradas/2026-05-02.md` § Entrada 002.  
> Commit: `fda8c86` — 2026-05-02 09:00

| Campo | Valor |
|-------|-------|
| Herramienta | Cursor |
| Resultado | acierto |
| Spec SDD | `docs/specs/pipeline-esquema-db.md` |

### Prompt (optimizado)

```
Crear esquema PostgreSQL (patients, studies, predictions, pipeline, alertas),
documentar arquitectura de BD, seguir SDD y registrar en diario IA.
```

### Resumen

- 7 tablas + 5 ENUMs + 2 vistas; alineado con CSV clínico y enunciado (3 clases).
- Skills `@salle-sdd` y `@diario-ia` actualizados con rutas de referencia.
