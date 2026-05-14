# ML — TensorFlow (entrenamiento e inferencia)

**Estructura del módulo:** [`docs/estructura-repositorio.md`](../docs/estructura-repositorio.md#ml--inteligencia-artificial)

| Parte | Ruta | Uso |
|-------|------|-----|
| Servicio inferencia | `app/` | FastAPI en Docker (`:8001`) |
| Entrenamiento offline | `scripts/` | ResNet50, comparativa arquitecturas |
| Exploración | `notebooks/` | Informe y matrices |
| Artefactos | `models/` | `.h5`, `reports/`, checkpoints (ver `.gitignore`) |

## Arranque inferencia (Docker)

```bash
docker compose up -d ml
curl http://localhost:8001/health
```

Requiere `ml/models/rx_resnet50_v1.h5` en el volumen montado.

## Entrenamiento

Ver [`docs/ml/resultados-entrenamiento-v1.md`](../docs/ml/resultados-entrenamiento-v1.md) y spec [`docs/specs/ml-entrenamiento.md`](../docs/specs/ml-entrenamiento.md).

```bash
docker compose run --rm --no-deps \
  -v ./data:/opt/data -v ./ml/models:/app/models \
  -e FEATURES_ROOT=/opt/data/processed/features \
  ml python scripts/train_resnet50.py
```
