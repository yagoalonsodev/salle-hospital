# Datos — salle-hospital

Estructura alineada con `enunciado.md` y `docs/specs/pipeline-datos-ejemplo.md`.

## Árbol

```text
data/
├── raw/                              # Entrada (no versionado en bloque)
│   ├── covid19_vs_pneumonia/         # RX: train|test / COVID19|NORMAL|PNEUMONIA
│   │   └── manifest.csv            # Una fila por imagen + label unificada
│   └── clinical/                     # CSV simulados (ingesta Spark)
│       ├── patients.csv
│       ├── studies.csv
│       └── pipeline_events.csv
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

## Regenerar CSV

Tras mover o añadir imágenes en `raw/covid19_vs_pneumonia/`:

```bash
python scripts/build_clinical_data.py
```

## Fuentes

| Fuente | Uso | Clases |
|--------|-----|--------|
| COVID-19 vs Pneumonia (Kaggle-style) | Entrenamiento MVP | sana, neumonia, covid |
| NIH Chest X-rays (opcional) | Más `No Finding` / 2ª fuente | Solo documentar si se añade |

## MinIO (runtime)

En Docker, las RX se copiarán a `xray-images/raw/` en MinIO (D2-04).
