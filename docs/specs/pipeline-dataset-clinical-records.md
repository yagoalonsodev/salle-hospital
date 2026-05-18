# Spec: Dataset clínico textual (100k registros)

| Meta | Valor |
|------|-------|
| Estado | hecho |
| Módulo | pipeline / scripts |
| BACKLOG | D10-CL-01 |

## 1. Descripción funcional

Generar un **dataset independiente** de las radiografías (`covid19_vs_pneumonia`): ~100 000 filas con datos simulados de paciente (nombre, edad, sexo), síntomas en texto libre y diagnóstico de referencia (ground truth). Alimenta el modelo de predicción por síntomas y la ingesta opcional a PostgreSQL.

## 2. Inputs

| Input | Tipo | Origen |
|-------|------|--------|
| `RECORDS_COUNT` | int (env) | Default 100 000 |
| Plantillas de síntomas | código | `scripts/build_clinical_records_dataset.py` |

## 3. Outputs

| Output | Tipo | Destino |
|--------|------|---------|
| `records.csv` | CSV | `data/raw/clinical_records/records.csv` |
| Metadatos | JSON | `data/raw/clinical_records/dataset_meta.json` |

Columnas CSV: `record_id`, `patient_ref`, `display_name`, `age`, `sex`, `symptoms`, `diagnosis`, `recorded_at`.

## 4. Restricciones

### Técnicas

- No mezclar filas con el manifest de RX; carpeta `data/raw/clinical_records/` separada de `data/raw/clinical/` (metadatos RX).
- Datos **simulados** (sin PII real).

### Negocio / clínicas

- Diagnósticos: `sana`, `neumonia`, `covid`, `gripe`, `asma`, `bronquitis`, `epoc`, `rinitis_alergica`.
- Distribución de clases aproximadamente balanceada.

## 5. Criterios de aceptación

- [x] Script genera ≥100 000 filas reproducibles (`seed=42`).
- [x] CSV con columnas acordadas y `dataset_meta.json`.
- [x] Documentado en `data/README.md`.

## 6. Prompt base para la IA

```text
Crear dataset de 100k líneas con pacientes (nombre, edad, género, síntomas, diagnosis)
APARTE de las radiografías. Dos datasets distintos.
```

## 7. Notas de implementación

- Script: `scripts/build_clinical_records_dataset.py`
- Job ingesta Spark opcional: `pipeline/jobs/ingest_clinical_records.py`
