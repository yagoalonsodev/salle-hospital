# Pipeline PySpark — salle-hospital

## Job: ingesta, validación y deduplicación de imágenes

Spec: [`docs/specs/pipeline-ingesta-imagenes-calidad.md`](../docs/specs/pipeline-ingesta-imagenes-calidad.md)

### Qué hace

1. **Carga automática** — escanea `data/raw/covid19_vs_pneumonia/**/*.jpg`
2. **Validación** — tamaño mínimo y cabecera JPEG (`FFD8FF`)
3. **Deduplicación** — elimina duplicados por hash MD5 del contenido
4. **Salida** — `data/processed/manifest/validated.parquet` (+ CSV)
5. **MinIO** — sube imágenes válidas a `{bucket}/raw/{hash}.jpg`
6. **Postgres** — registra `pipeline_runs`, eventos e incidencias (si `DATABASE_URL` está definida)

### Ejecutar (stack Docker levantado)

```bash
docker exec salle-pipeline /opt/spark/bin/spark-submit \
  --master spark://spark-master:7077 \
  --driver-memory 2g \
  /opt/pipeline/jobs/ingest_validate_images.py
```

### Variables de entorno

| Variable | Default |
|----------|---------|
| `RAW_IMAGES_GLOB` | `/opt/data/raw/covid19_vs_pneumonia/*/*/*.jpg` |
| `PROCESSED_MANIFEST_DIR` | `/opt/data/processed/manifest` |
| `UPLOAD_MINIO` | `true` |
| `MINIO_ENDPOINT` | `minio:9000` |
| `DATABASE_URL` | (compose) |
| `MAX_UPLOAD` | `0` (= todas; usar `100` para prueba rápida MinIO) |

### Informe

Tras ejecutar, ver `data/processed/manifest/ingest_report.json`.

### Verificación (Postgres + MinIO)

```bash
# Tras el job (desde el host, con stack levantado):
docker exec -e DATABASE_URL=postgresql://salle:salle_secret@postgres:5432/salle_hospital \
  -e MINIO_ENDPOINT=minio:9000 \
  salle-pipeline python3 /opt/scripts/verify_pipeline_integration.py
```

### Alineación con el enunciado

| Requisito (`enunciado.md`) | Cobertura |
|----------------------------|-----------|
| Ingesta automatizada | Escaneo manifest / árbol raw |
| Almacenamiento no estructurado | MinIO `xray-images/raw/{hash}.jpg` |
| Validación calidad (corruptos, duplicados) | JPEG + MD5 dedup → `rejected.parquet` |
| Logging / monitorización | `pipeline_runs`, `pipeline_events`, `data_quality_issues` |
| PySpark escalable | Job en cluster Spark (`spark-master`) |
