# Índice — Diario IA

Documento obligatorio del encargo (`enunciado.md`). Cada día con desarrollo tiene al menos una entrada en `entradas/YYYY-MM-DD.md`, alineada con `git log` y specs en `docs/specs/`.

**Convención:** fecha del archivo = fecha del commit principal (`git log --date=short`). Prompts tomados de sesiones SDD (`.cursor/skills/salle-sdd/sessions/`) y entradas existentes.

---

## Calendario de entradas

| Fecha | Día práctica | Entradas | Archivo |
|-------|--------------|----------|---------|
| 2026-05-01 | D1 Infra | 001 Docker compose · 002 Skills SDD/diario | [2026-05-01.md](entradas/2026-05-01.md) |
| 2026-05-02 | D2 Datos + pipeline | 001–006 datos, esquema, ingesta, watcher | [2026-05-02.md](entradas/2026-05-02.md) |
| 2026-05-03 | D3 Preprocesado | 001 PySpark preprocess · 002 Seguridad | [2026-05-03.md](entradas/2026-05-03.md) |
| 2026-05-04 | D4 Arquitectura ML | 001 ResNet50 + justificación | [2026-05-04.md](entradas/2026-05-04.md) |
| 2026-05-05 | D5 Entrenamiento | 001 Comparativa 4 arquitecturas | [2026-05-05.md](entradas/2026-05-05.md) |
| 2026-05-06 | D6 API Flask | 001 API + UI + ML | [2026-05-06.md](entradas/2026-05-06.md) |
| 2026-05-07 | D7 Dashboard | 001 Streamlit + robustez | [2026-05-07.md](entradas/2026-05-07.md) |
| 2026-05-08 | D8 Monitorización | 001 Calidad y alertas | [2026-05-08.md](entradas/2026-05-08.md) |
| 2026-05-09 | D9 Documentación | 001 Memoria, diagramas, ética | [2026-05-09.md](entradas/2026-05-09.md) |
| 2026-05-10 | D10 Presentación | 001 Guion y demo (parcial) | [2026-05-10.md](entradas/2026-05-10.md) |
| 2026-05-11 – 13 | — | Sin commits en repo | — |
| 2026-05-14 | Cierre D2-03 | 001 CSV → Postgres | [2026-05-14.md](entradas/2026-05-14.md) |
| 2026-05-15 – 17 | — | Sin commits en repo | — |
| 2026-05-18 | Verificación + Airflow + logs | 001–005 verify_stack, Airflow, índice, MongoDB, dashboard logs | [2026-05-18.md](entradas/2026-05-18.md) |

---

## Detalle por archivo (anclas)

| Fecha | Título | Enlace |
|-------|--------|--------|
| 2026-05-01 | Infra Docker y compose | [entrada 001](entradas/2026-05-01.md#entrada-001--infra-docker-y-stack-compose) |
| 2026-05-01 | Diario IA, SDD y backlog | [entrada 002](entradas/2026-05-01.md#entrada-002--diario-ia-sdd-y-backlog-del-proyecto) |
| 2026-05-02 | Datos, esquema, ingesta, watcher | [archivo](entradas/2026-05-02.md) |
| 2026-05-03 | Preprocesado RX | [entrada 001](entradas/2026-05-03.md#entrada-001--preprocesado-rx-para-entrenamiento-día-3) |
| 2026-05-03 | Seguridad y secretos | [entrada 002](entradas/2026-05-03.md#entrada-002--skill-seguridad-y-secretos-fuera-del-código-sdd) |
| 2026-05-04 | Arquitectura ML ResNet50 | [entrada 001](entradas/2026-05-04.md#entrada-001--arquitectura-ml-transfer-learning--resnet50-día-4) |
| 2026-05-05 | Comparativa 4 arquitecturas | [entrada 001](entradas/2026-05-05.md#entrada-001--informe-día-5-comparativa-4-arquitecturas-y-conclusión-memoria) |
| 2026-05-06 | API Flask y UI | [entrada 001](entradas/2026-05-06.md#entrada-001--día-6-api-flask-pacientes-ui-radiografías-e-integración-ml) |
| 2026-05-07 | Dashboard Streamlit | [entrada 001](entradas/2026-05-07.md#entrada-001--día-7-dashboard-streamlit-visualización-y-robustez) |
| 2026-05-08 | Monitorización D8 | [entrada 001](entradas/2026-05-08.md#entrada-001--día-8-monitorización-y-calidad-de-datos) |
| 2026-05-09 | Memoria y documentación | [entrada 001](entradas/2026-05-09.md#entrada-001--día-9-documentación-memoria-técnica-y-cierre-documental) |
| 2026-05-10 | Presentación (guion) | [entrada 001](entradas/2026-05-10.md#entrada-001--día-10-preparación-de-presentación-y-demo-sin-código-nuevo) |
| 2026-05-14 | D2-03 CSV Postgres | [entrada 001](entradas/2026-05-14.md#entrada-001--cierre-d2-03-backlog-y-verificación-del-stack) |
| 2026-05-18 | verify_stack.sh | [entrada 001](entradas/2026-05-18.md#entrada-001--script-verify_stacksh-un-comando-levanta-y-prueba-todo) |
| 2026-05-18 | Airflow UI :8081 | [entrada 002](entradas/2026-05-18.md#entrada-002--airflow-ui-en-8081-webserver-login-short-circuit-dag) |
| 2026-05-18 | MongoDB logs centralizados | [entrada 004](entradas/2026-05-18.md#entrada-004--mongodb-centralizada-para-todos-los-logs) |
| 2026-05-18 | Dashboard → logs Mongo | [entrada 005](entradas/2026-05-18.md#entrada-005--logs-del-dashboard-movidos-a-mongodb) |
| 2026-05-10 | Presentación D10 | [entrada 001](entradas/2026-05-10.md) |

---

## Sesiones SDD (prompts de referencia)

| Fecha | Sesión |
|-------|--------|
| 2026-05-01 | `.cursor/skills/salle-sdd/sessions/2026-05-01-skills-diario.md` |
| 2026-05-02 | `2026-05-02-datos-ejemplo.md`, `esquema-db.md`, `ingesta-imagenes.md`, `watcher-airflow.md`, `verificacion-integracion.md` |
| 2026-05-03 | `2026-05-03-preprocesado-imagenes.md` |
| 2026-05-04 | `2026-05-04-arquitectura-ml.md` |
| 2026-05-05 | `2026-05-05-informe-arquitecturas.md` |
| 2026-05-06 | `2026-05-06-api-flask-ui.md` |
| 2026-05-07 | `2026-05-07-dashboard-robustez.md` |

---

## Commits de referencia (extracto)

| Fecha | Hash | Mensaje |
|-------|------|---------|
| 2026-05-01 | `2473592` | infra: stack completo |
| 2026-05-02 | `c753caa` | watcher + DAG Airflow |
| 2026-05-03 | `0818bd9` | preprocess_images |
| 2026-05-03 | `c95ce67` | docs(ml) Día 4 arquitectura |
| 2026-05-05 | `a142a2c` | comparativa 4 arquitecturas |
| 2026-05-06 | `c8f20a3` | feat(api) Día 6 |
| 2026-05-07 | `3620d07` | feat(dashboard) Día 7 |
| 2026-05-08 | `ec0db53` | feat(ops) Día 8 |
| 2026-05-09 | `d3f066a` | docs Día 9 |
| 2026-05-14 | `0d38942` | feat(pipeline) D2-03 CSV |
| 2026-05-18 | `9ffe6cc` | chore(ops) verify_stack |
| 2026-05-18 | `f16089f` | feat(ops) MongoDB logs + log-sync |

---

_Total entradas canónicas: 20 (en 12 archivos por día)_
