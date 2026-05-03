# Sesión SDD — Preprocesado imágenes Día 3 (2026-05-03)

> Spec: `docs/specs/pipeline-preprocesado-imagenes.md`

## Entregables

| Artefacto | Ruta |
|-----------|------|
| Job PySpark | `pipeline/jobs/preprocess_images.py` |
| Transforms | `pipeline/jobs/image_transforms.py` |
| Justificación | `docs/preprocess-distributed-justification.md` |
| Dataset | `data/processed/features/v1/` |
| Informe | `preprocess_report.json` (19446 muestras) |

## Resultado verificado

- 6399 imágenes fuente → 19446 muestras (aug ×4 en train).
- Spark workers con Pillow (`infra/spark/Dockerfile`).
