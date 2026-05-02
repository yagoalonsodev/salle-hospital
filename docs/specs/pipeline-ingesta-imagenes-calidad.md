# Spec: Ingesta automática de imágenes, validación y deduplicación

| Meta | Valor |
|------|-------|
| Estado | implementada |
| Módulo | pipeline (PySpark) |
| BACKLOG | D2-04, D2-05 |

## 1. Descripción funcional

Job PySpark que **escanea** `data/raw/covid19_vs_pneumonia/`, **valida** cada JPG (tamaño, cabecera), **elimina duplicados** por hash de contenido, **sube** imágenes válidas a MinIO y escribe manifiestos en `data/processed/`. Registra incidencias de calidad y resumen del run en PostgreSQL (opcional).

## 2. Inputs

| Input | Tipo | Origen |
|-------|------|--------|
| Imágenes JPG | binario | `data/raw/covid19_vs_pneumonia/**/*.jpg` |
| Config | env | `SPARK_MASTER_URL`, `MINIO_*`, `DATABASE_URL` |

## 3. Outputs

| Output | Tipo | Destino |
|--------|------|---------|
| Manifiesto válido | Parquet + CSV | `data/processed/manifest/validated.*` |
| Rechazados | Parquet | `data/processed/manifest/rejected.*` |
| Objetos RX | JPG | MinIO `xray-images/raw/{content_hash}.jpg` |
| Calidad / run | SQL | `data_quality_issues`, `pipeline_runs`, `pipeline_events` |

## 4. Reglas de calidad

| Regla | `issue_type` | Acción |
|-------|--------------|--------|
| Archivo vacío o &lt; 500 bytes | `corrupt` | Rechazar |
| Cabecera no JPEG (`FFD8FF`) | `corrupt` | Rechazar |
| Mismo MD5 que otro archivo | `duplicate` | Mantener uno (ruta lexicográfica menor) |
| Ruta sin split/clase válida | `incomplete` | Rechazar |

## 5. Criterios de aceptación

- [x] Carga automática recursiva sin listar manualmente cada archivo.
- [x] Validación de corruptos y duplicados.
- [x] Salida en `data/processed/manifest/`.
- [x] Subida a MinIO si el servicio está disponible.
- [x] Ejecutable con `spark-submit` en contenedor `salle-pipeline`.
- [x] Verificado E2E: Postgres (`pipeline_runs`, eventos, calidad) y MinIO (`xray-images/raw/`).

## 7. Normalización de formato

Antes del job, ejecutar `scripts/convert_rx_to_jpeg.py` si hay `.jpg` que no son JPEG (p. ej. PNG renombrados). El dataset COVID tenía 215 casos; tras conversión, 6432 cabeceras JPEG válidas.

## 8. Verificación (2026-05-02)

```bash
scripts/verify_pipeline_integration.py  # vía contenedor pipeline
```

Resultado: ~6400 válidas únicas (solo duplicados MD5 en rechazos); MinIO y Postgres OK (ver sesión SDD `2026-05-02-verificacion-integracion.md`).

## 6. Prompt base

```text
Implementar job PySpark ingest_validate_images: escanear raw RX, validar JPG,
deduplicar por MD5, subir a MinIO, escribir manifest procesado y log en Postgres.
```
