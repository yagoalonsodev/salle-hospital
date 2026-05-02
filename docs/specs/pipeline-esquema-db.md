# Spec: Esquema PostgreSQL (salle_hospital)

| Meta | Valor |
|------|-------|
| Estado | implementada |
| Módulo | infra / pipeline |
| BACKLOG | D2-01 |

## 1. Descripción funcional

Definir el modelo relacional en PostgreSQL para la aplicación hospitalaria: pacientes y estudios de RX (metadatos), predicciones del modelo DL, ejecuciones del pipeline, eventos/logs, incidencias de calidad de datos y alertas para el dashboard.

## 2. Inputs

| Input | Tipo | Origen |
|-------|------|--------|
| CSV clínico | `patients`, `studies`, `pipeline_events` | `data/raw/clinical/` |
| Predicciones ML | JSON / filas | Servicio `ml` (futuro) |
| Resultados Spark | métricas de job | Jobs `pipeline` (futuro) |

## 3. Outputs

| Output | Tipo | Destino |
|--------|------|---------|
| DDL inicial | SQL | `infra/postgres/01-init-salle-schema.sql` |
| Documentación | Markdown | `docs/database-architecture.md` |
| BD en runtime | PostgreSQL 16 | DB `salle_hospital` (compose) |

## 4. Restricciones

- Compatible con PostgreSQL 16 (Alpine en Docker).
- Script en `docker-entrypoint-initdb.d` (solo primera creación del volumen).
- Etiquetas alineadas con CSV: `sana`, `neumonia`, `covid`.
- Datos simulados; sin PHI real.
- BD `airflow` separada (script `02-init-airflow-db.sql`).

## 5. Criterios de aceptación

- [x] Tablas: `patients`, `studies`, `predictions`, `pipeline_runs`, `pipeline_events`, `data_quality_issues`, `alerts`.
- [x] ENUMs, FKs e índices básicos.
- [x] Documento de arquitectura de BD.
- [x] Montaje en `docker-compose.yml`.
- [ ] Job de ingesta CSV → tablas (D2-03).

## 6. Prompt base

```text
Crear esquema PostgreSQL según docs/architecture.md y CSV en data/raw/clinical/,
documentar en docs/database-architecture.md, init en infra/postgres/.
```
