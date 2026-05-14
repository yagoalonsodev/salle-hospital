# Datos — salle-hospital

**Estructura canónica:** [`docs/estructura-repositorio.md`](../docs/estructura-repositorio.md#data--datos-locales-volumen-docker) (sección `data/`).  
Specs: [`docs/specs/pipeline-datos-ejemplo.md`](../docs/specs/pipeline-datos-ejemplo.md).

## Árbol `data/` (resumen)

```text
data/
├── raw/
│   ├── clinical/                     # studies.csv, pipeline_events.csv
│   └── covid19_vs_pneumonia/
│       ├── manifest.csv
│       ├── incoming/                 # Bandeja watcher → DAG Airflow
│       ├── train/{NORMAL,PNEUMONIA,COVID19}/
│       └── test/{NORMAL,PNEUMONIA,COVID19}/
└── processed/
    ├── manifest/                     # validated/rejected parquet, ingest_report
    ├── features/v1/                  # RX 224×224 por split/label (ML)
    └── watcher/                      # pending.flag, events.jsonl
```

Los `.jpg` masivos están en `.gitignore`; ver volúmenes en `README.md`.

## Etiquetas ML

| Carpeta | `label` |
|---------|---------|
| `NORMAL` | `sana` |
| `PNEUMONIA` | `neumonia` |
| `COVID19` | `covid` |

## Normalizar JPEG

Si hay `.jpg` que no son JPEG real (p. ej. PNG del dataset Kaggle):

```bash
docker exec salle-pipeline pip install -q Pillow
docker exec salle-pipeline python3 /opt/scripts/convert_rx_to_jpeg.py
```

Informe: `data/processed/manifest/conversion_report.json`.

## Regenerar CSV

Tras mover, convertir o añadir imágenes en `raw/covid19_vs_pneumonia/`:

```bash
python scripts/build_clinical_data.py
```

## Fuentes

| Fuente | Uso | Clases |
|--------|-----|--------|
| COVID-19 vs Pneumonia (Kaggle-style) | Entrenamiento MVP | sana, neumonia, covid |
| NIH Chest X-rays (opcional) | Más `No Finding` / 2ª fuente | Solo documentar si se añade |

## Bandeja de nuevas imágenes (watcher)

Copia RX en `raw/covid19_vs_pneumonia/incoming/train/NORMAL/` (u otra clase). El servicio `salle-watcher` las mueve al árbol y el DAG Airflow `salle_rx_pipeline` procesa la cola. Ver [`incoming/README.md`](raw/covid19_vs_pneumonia/incoming/README.md) y [`airflow/README.md`](../airflow/README.md).

## Dataset procesado para ML (Día 3)

Tras `preprocess_images.py`:

```text
data/processed/features/v1/
  train/{sana,neumonia,covid}/*.jpg      # con augmentation
  validation/{...}/*.jpg                 # solo original
  test/{...}/*.jpg
  dataset_index.parquet
  preprocess_report.json
```

Ver [`pipeline/README.md`](../pipeline/README.md) y [`docs/preprocess-distributed-justification.md`](../docs/preprocess-distributed-justification.md).

## Pipeline de imágenes (PySpark)

```bash
docker exec salle-pipeline /opt/spark/bin/spark-submit \
  --master spark://spark-master:7077 \
  /opt/pipeline/jobs/ingest_validate_images.py
```

Salida: `data/processed/manifest/validated.parquet`, `rejected.parquet`, `ingest_report.json`.  
Ver [`pipeline/README.md`](../pipeline/README.md).
