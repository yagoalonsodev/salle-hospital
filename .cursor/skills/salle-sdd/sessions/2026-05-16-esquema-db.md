# Sesión SDD — Esquema PostgreSQL (2026-05-16)

## Flujo aplicado

1. BACKLOG **D2-01** → spec `docs/specs/pipeline-esquema-db.md`
2. DDL `infra/postgres/01-init-salle-schema.sql`
3. Documentación `docs/database-architecture.md`
4. `docker-compose.yml` monta script `01` antes de Airflow `02`
5. BACKLOG: D2-01 → **hecho**

## Artefactos

| Artefacto | Ruta |
|-----------|------|
| Spec | `docs/specs/pipeline-esquema-db.md` |
| Init SQL | `infra/postgres/01-init-salle-schema.sql` |
| Doc BD | `docs/database-architecture.md` |

## Pendiente

- D2-03: ingesta CSV → tablas
- Aplicar schema en volumen Postgres existente (`psql` manual o `down -v`)
