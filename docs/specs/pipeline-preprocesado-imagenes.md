# Spec: Preprocesado de imágenes RX para entrenamiento (Día 3)

| Meta | Valor |
|------|-------|
| Estado | implementado |
| Módulo | pipeline |
| BACKLOG | D3-01, D3-02, D3-03 |

## 1. Descripción funcional

Job PySpark que toma imágenes validadas del manifest, aplica **redimensionado**, **normalización**, **data augmentation** (solo train) y genera un dataset en `data/processed/features/` con splits **train / validation / test** listo para TensorFlow.

## 2. Inputs / outputs

| Input | Origen |
|-------|--------|
| `validated.parquet` o `manifest.csv` | `data/processed/manifest/` |
| JPG en `data/raw/covid19_vs_pneumonia/` | Filesystem |

| Output | Destino |
|--------|---------|
| Imágenes 224×224 JPEG | `data/processed/features/v1/{split}/{label}/` |
| Índice del dataset | `dataset_index.parquet` + `dataset_index.csv` |
| Informe | `preprocess_report.json` |

## 3. Transformaciones

| Paso | Train | Validation | Test |
|------|-------|------------|------|
| Redimensionar 224×224 | Sí | Sí | Sí |
| Normalización [0,1] → uint8 | Sí | Sí | Sí |
| Rotación ±15° | Augment | No | No |
| Flip horizontal | Augment | No | No |
| Zoom 1.1× crop | Augment | No | No |

Split: el split `test` del dataset original se mantiene; `train` se divide 85/15 en train/validation (semilla fija).

## 4. Justificación PySpark (dataset pequeño)

Ver [docs/preprocess-distributed-justification.md](../preprocess-distributed-justification.md).

## 5. Criterios de aceptación

- [x] Salida reproducible con `IMAGE_SIZE`, `VAL_RATIO`, `RANDOM_SEED` en entorno.
- [x] Tres splits con carpetas por etiqueta (`sana`, `neumonia`, `covid`).
- [x] Augmentations solo en train.
- [x] Ejecutable con `spark-submit` en `salle-pipeline`.
- [x] `preprocess_report.json` con conteos por split/label.

## 6. Prompt base

```text
Implementar preprocess_images.py con PySpark: resize, normalización,
augmentation (rot, flip, zoom) en train, split train/val/test,
salida en data/processed/features/v1/.
```
