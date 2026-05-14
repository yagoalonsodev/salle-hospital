# Spec: Ingesta CSV clínico → PostgreSQL (PySpark)

| Meta | Valor |
|------|-------|
| Estado | implementado |
| Módulo | pipeline |
| BACKLOG | D2-03 |

## 1. Descripción funcional

Job PySpark que lee `data/raw/clinical/studies.csv` (y opcionalmente `pipeline_events.csv`), deriva filas de `patients` (1:1 por `patient_id` en studies) y hace **upsert** masivo en PostgreSQL con registro en `pipeline_runs` / `pipeline_events`.

## 2. Inputs

| Input | Origen |
|-------|--------|
| `studies.csv` | `scripts/build_clinical_data.py` → `data/raw/clinical/` |
| `pipeline_events.csv` | mismo script (opcional) |
| `DATABASE_URL` | entorno Docker / pipeline |

## 3. Outputs

| Output | Tabla |
|--------|-------|
| Pacientes derivados | `patients` |
| Estudios del dataset RX | `studies` |
| Eventos simulados | `pipeline_events` |
| Trazas | `pipeline_runs`, `data_quality_issues` |

## 4. Criterios de aceptación

- [x] Job `pipeline/jobs/ingest_csv_to_postgres.py`
- [x] Validación de columnas, label y split
- [x] Upsert idempotente (`ON CONFLICT`)
- [x] Registro en `pipeline_runs` vía `db_log`

## 5. Ejecución

```bash
docker exec salle-pipeline /opt/spark/bin/spark-submit \
  --master spark://spark-master:7077 \
  /opt/pipeline/jobs/ingest_csv_to_postgres.py
```
