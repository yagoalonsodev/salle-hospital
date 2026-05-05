# Spec: Entrenamiento ResNet50 — clasificación RX (Día 5)

| Meta | Valor |
|------|-------|
| Estado | implementado |
| Módulo | ml |
| BACKLOG | D4-03 |

## 1. Descripción funcional

Entrenar la primera versión del clasificador **ResNet50 + Transfer Learning** sobre `data/processed/features/v1/`, guardar checkpoints, exportar **`.h5`** y **SavedModel**, y generar informes de métricas y gráficos.

## 2. Inputs / outputs

| Input | Origen |
|-------|--------|
| Imágenes por split/label | `features/v1/{train,validation,test}/` |
| Arquitectura | `ml/models/architectures.py` |

| Output | Destino |
|--------|---------|
| Modelo Keras | `ml/models/rx_resnet50_v1.h5` |
| SavedModel | `ml/models/savedmodel/rx_resnet50_v1/` |
| Checkpoints | `ml/models/checkpoints/` |
| Informe JSON | `ml/models/reports/training_report_v1.json` |
| Gráficos | `confusion_matrix_test.png`, `training_curves.png` |
| Análisis clínico | `docs/ml/evaluacion-clinica-v1.md` |

## 3. Entrenamiento

| Fase | Backbone | LR | Épocas máx. |
|------|----------|-----|-------------|
| 1 — cabeza | Congelado | 1e-3 | 10 |
| 2 — fine-tune | Últimas ~40 capas | 1e-5 | 8 |

- Optimizer: Adam  
- Loss: `sparse_categorical_crossentropy`  
- **Class weights** por desbalance (más peso a `covid`)  
- Callbacks: `ModelCheckpoint`, `EarlyStopping`, `CSVLogger`

## 4. Formato del modelo (requisito encargo)

El **enunciado no exige `.pt` ni `.h5`**. Exige modelo en el sistema Docker + evaluación en memoria.

| Formato | Framework | Uso en este proyecto |
|---------|-----------|----------------------|
| `.h5` | TensorFlow/Keras | Entregable pesos + arquitectura (memoria, backup) |
| **SavedModel** | TensorFlow | Servicio `ml` en Docker (inferencia) |
| `.pt` | PyTorch | **No usado** (stack elegido: TensorFlow, ver `docs/architecture.md`) |

## 5. Criterios de aceptación

- [x] Script `ml/scripts/train_resnet50.py` ejecutable con datos v1.
- [x] Checkpoints y mejor modelo guardados.
- [x] Métricas test: accuracy, precision, recall, F1 (por clase y macro).
- [x] Matriz de confusión y curvas de entrenamiento exportadas.
- [x] Documento FP/FN e impacto clínico.

## 6. Comparativa de arquitecturas (Día 5)

Protocolo común (`ml/scripts/training_core.py`): mismo dataset v1, class weights, fases cabeza + fine-tune, evaluación en test (n=1285).

| Arquitectura | Accuracy test | F1 macro | FN neumonía→sana | Notas |
|--------------|---------------|----------|------------------|-------|
| DenseNet121 | 93,2 % | **93,4 %** | 72 | Ganador ranking F1 |
| ResNet50 | **94,0 %** | 93,1 % | **37** | **Modelo operativo** (`rx_resnet50_v1`) |
| Baseline CNN | 87,7 % | 87,8 % | 118 | Línea base encargo |
| EfficientNetB0 | 66,4 % | 26,6 % | — | Entrenamiento inestable; no despliegue |

**Decisión:** DenseNet121 ligeramente superior en F1 macro; ResNet50 se mantiene en producción por menor FN crítico, mayor accuracy e integración Docker.

Artefactos: `ml/models/reports/architecture_comparison.json`, informe en `ml/notebooks/01_exploracion_arquitectura.ipynb`.

## 7. Ejecución

```bash
docker compose build ml
docker compose run --rm \
  -v ./data:/opt/data \
  -e FEATURES_ROOT=/opt/data/processed/features \
  -e FEATURES_VERSION=v1 \
  ml python scripts/train_resnet50.py
```
