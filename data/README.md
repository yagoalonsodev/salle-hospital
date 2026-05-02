# Datos — salle-hospital

Estructura alineada con `enunciado.md` y `docs/specs/pipeline-datos-ejemplo.md`.

## Árbol

```text
data/
├── raw/                              # Entrada (no versionado en bloque)
│   ├── covid19_vs_pneumonia/         # RX: train|test / COVID19|NORMAL|PNEUMONIA
│   │   └── manifest.csv            # Una fila por imagen + label unificada
│   └── clinical/                     # CSV derivados del dataset RX (ingesta Spark)
│       ├── studies.csv               # Una fila por imagen (+ patient_id opaco)
│       └── pipeline_events.csv       # Log simulado de ingesta
└── processed/                        # Salida ETL / preprocesado ML
    ├── manifest/
    └── features/

ml/models/                            # SavedModel TensorFlow (no en data/)
```

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

## Pipeline de imágenes (PySpark)

```bash
docker exec salle-pipeline /opt/spark/bin/spark-submit \
  --master spark://spark-master:7077 \
  /opt/pipeline/jobs/ingest_validate_images.py
```

Salida: `data/processed/manifest/validated.parquet`, `rejected.parquet`, `ingest_report.json`.  
Ver [`pipeline/README.md`](../pipeline/README.md).
