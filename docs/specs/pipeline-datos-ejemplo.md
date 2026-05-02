# Spec: Datos de ejemplo (raw + clínico simulado)

| Meta | Valor |
|------|-------|
| Estado | implementada |
| Módulo | pipeline / data |
| BACKLOG | D2-02 |

## 1. Descripción funcional

Preparar datos locales alineados con `enunciado.md` y `docs/architecture.md`: radiografías en tres clases (sana, neumonía, COVID-19), CSV clínico/operativo simulado para ingesta Spark → PostgreSQL, y carpetas `data/raw` y `data/processed`. El modelo entrenado vive en `ml/models/`, no en `data/`.

## 2. Inputs

| Input | Tipo | Origen |
|-------|------|--------|
| Imágenes RX | JPG | Dataset público COVID-19 vs Pneumonia (`train/` + `test/`) |
| Metadatos generados | CSV | Script `scripts/build_clinical_data.py` |

## 3. Outputs

| Output | Tipo | Destino |
|--------|------|---------|
| Imágenes organizadas | JPG | `data/raw/covid19_vs_pneumonia/{train,test}/{COVID19,NORMAL,PNEUMONIA}/` |
| Manifiesto de imágenes | CSV | `data/raw/covid19_vs_pneumonia/manifest.csv` |
| Estudios / RX | CSV | `data/raw/clinical/studies.csv` (incluye `patient_id` opaco 1:1) |
| Logs operativos | CSV | `data/raw/clinical/pipeline_events.csv` |
| Salida ETL (futuro) | Parquet/CSV | `data/processed/` |

## 4. Restricciones

### Técnicas

- Rutas sin espacios bajo `data/raw/`.
- Datos raw en `.gitignore`; solo scripts y README versionados.
- Etiquetas unificadas: `sana`, `neumonia`, `covid` (mapeo desde carpetas originales).
- Segunda fuente (NIH) **opcional**; documentar en memoria si se añade después.

### Negocio / clínicas

- Datos **simulados/anonimizados**; no datos reales de pacientes.
- Desequilibrio de clases documentado (más neumonía que COVID).

## 5. Criterios de aceptación

- [x] Dataset RX en `data/raw/covid19_vs_pneumonia/` con 3 clases y splits train/test.
- [x] CSV `studies`, `pipeline_events` en `data/raw/clinical/` (sin `patients.csv`).
- [x] `manifest.csv` con una fila por imagen y etiqueta unificada.
- [x] `data/processed/` preparado para salida Spark/ML.
- [x] `ml/models/` reservado para SavedModel (sin pesos en repo).
- [ ] Ingesta a Postgres + MinIO (D2-03, D2-04).

## 6. Mapeo de etiquetas

| Carpeta original | `label` (ML) | Enunciado |
|------------------|--------------|-----------|
| `NORMAL` | `sana` | Sana |
| `PNEUMONIA` | `neumonia` | Neumonía |
| `COVID19` | `covid` | COVID-19 |

## 7. Inventario (2026-05-01)

| Clase | Train | Test | Total |
|-------|------:|-----:|------:|
| neumonia | 3418 | 855 | 4273 |
| sana | 1266 | 317 | 1583 |
| covid | 460 | 116 | 576 |
| **Total** | | | **6432** |

## 8. Prompt base para la IA

```text
Reorganiza datos según docs/specs/pipeline-datos-ejemplo.md:
mover RX a data/raw/covid19_vs_pneumonia, generar CSV clínico simulado
(studies, pipeline_events) y manifest, mantener ml/models para SavedModel.
```

## 9. Notas de implementación

- Script: `scripts/build_clinical_data.py`
- Documentación: `data/README.md`
