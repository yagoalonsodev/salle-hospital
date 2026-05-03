# Justificación técnica — preprocesado distribuido con PySpark

## Contexto

El dataset COVID-19 vs Pneumonia tiene ~6.400 radiografías: volumen **moderado**, no “big data” en sentido estricto. Aun así el encargo exige un **framework escalable** (Spark) y un pipeline reproducible alineado con el resto del hospital (ingesta, calidad, orquestación Airflow).

## Por qué PySpark y no solo un script Pillow local

| Motivo | Explicación |
|--------|-------------|
| **Misma stack que ingesta** | `ingest_validate_images.py` ya corre en el cluster `spark-master` / worker. Reutilizar sesión, particionado y logging evita un segundo runtime (Dask) solo para ~6k ficheros. |
| **Particionado embarazoso** | `mapPartitions` reparte miles de lecturas/escrituras de disco entre executors. En un portátil un único proceso Python serializa I/O; en Spark el paralelismo es configurable (`spark.sql.shuffle.partitions`, repartition por etiqueta). |
| **Escalabilidad horizontal** | Si el hospital añade NIH Chest X-ray u otra fuente (decenas o cientos de miles de RX), el mismo job aumenta particiones y workers sin reescribir la lógica. |
| **Reproducibilidad operativa** | Misma imagen Docker `salle-pipeline`, variables de entorno y trazas que el job de ingesta; integrable en un DAG Airflow futuro (`preprocess` tras `ingest`). |
| **Metadatos junto a binarios** | Spark escribe `dataset_index.parquet` con esquema tipado (split, label, augment_type, paths) para auditoría y para el módulo ML sin escanear directorios a mano. |

## Por qué no Dask en este proyecto

Dask encaja en pipelines **NumPy/pandas** puros. Aquí las imágenes ya viven en un flujo **Spark + manifest parquet + MinIO**. Introducir Dask duplicaría dependencias y orquestación sin beneficio claro en el MVP.

## Limitación honesta

Para ~6.400 imágenes, un script monolítico con `multiprocessing` sería más rápido en una máquina. La elección de Spark es **arquitectónica y pedagógica**: demostrar diseño distribuido, no maximizar FPS en un portátil.

## Parámetros de diseño

- Transformaciones CPU-bound (PIL) dentro de `mapPartitions` — patrón estándar “Spark orquesta, Python procesa”.
- Augmentation solo en **train** para no inflar validación/test ni sesgar métricas.
- Semilla fija (`RANDOM_SEED=42`) para split train/val reproducible.
