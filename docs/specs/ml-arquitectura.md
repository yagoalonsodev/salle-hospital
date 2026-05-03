# Spec: Arquitectura del modelo de clasificación RX (Día 4)

| Meta | Valor |
|------|-------|
| Estado | implementado |
| Módulo | ml |
| BACKLOG | D4-01 |

## 1. Descripción funcional

Investigar y fijar la arquitectura de Deep Learning para clasificar radiografías de tórax en **3 clases** (`sana`, `neumonia`, `covid`). Comparar CNN propia frente a Transfer Learning y evaluar backbones ResNet50, EfficientNetB0 y DenseNet121. Entregar documento de justificación y notebook exploratorio (sin entrenamiento completo).

## 2. Inputs / outputs

| Input | Origen |
|-------|--------|
| Dataset preprocesado 224×224 | `data/processed/features/v1/{train,validation,test}/{label}/` |
| Informe de preprocesado | `data/processed/features/v1/preprocess_report.json` |

| Output | Destino |
|--------|---------|
| Decisión de arquitectura | `docs/ml/arquitectura-rx.md` |
| Builders Keras reutilizables | `ml/models/architectures.py` |
| Notebook exploratorio | `ml/notebooks/01_exploracion_arquitectura.ipynb` |

## 3. Decisión

| Opción | Decisión |
|--------|----------|
| Enfoque | **Transfer Learning** (backbone ImageNet + cabeza densa 3 clases) |
| Backbone principal | **ResNet50** |
| Baseline | CNN propia pequeña (~1–2M parámetros) solo para comparación |
| Framework | TensorFlow 2 / Keras (`tensorflow.keras.applications`) |
| Formato modelo (Día 5) | **SavedModel** + opcional `.h5` (Keras); no PyTorch (`.pt`) |

### Estrategia de entrenamiento (Día 5)

1. Fase 1: backbone **congelado**, solo cabeza entrenable.
2. Fase 2: **fine-tuning** de las últimas capas del backbone (learning rate bajo).
3. Métricas: accuracy, precision, recall, F1, matriz de confusión, curvas loss/accuracy.

## 4. Restricciones

### Técnicas

- `IMAGE_SIZE=224` alineado con el pipeline Día 3.
- Entrada RGB; rescale `1/255` en el modelo (imágenes ya en uint8 JPEG).
- Sin secretos en código; artefactos de entrenamiento en `ml/models/` (gitignored).

### Clínicas / éticas

- Soporte a la decisión, no diagnóstico definitivo.
- Documentar falsos positivos/negativos e impacto clínico en Día 5 (`ml-evaluacion.md`).

## 5. Criterios de aceptación

- [x] Documento comparando CNN propia vs TL y ResNet / EfficientNet / DenseNet.
- [x] Elección explícita: ResNet50 + TL con argumentos para dataset médico pequeño.
- [x] Notebook carga muestras de `features/v1`, muestra `summary()` y conteo de parámetros.
- [x] Código `build_transfer_classifier(backbone="resnet50")` listo para Día 5.

## 6. Prompt base

```text
Día 4 ML: spec ml-arquitectura, docs/ml/arquitectura-rx.md, ml/models/architectures.py,
notebook 01_exploracion_arquitectura.ipynb. Decisión: Transfer Learning ResNet50.
Preprocesado ya en features/v1. Sin entrenamiento largo.
```

## 7. Notas

- D4-02 (preprocesado/aug) cubierto por [pipeline-preprocesado-imagenes.md](pipeline-preprocesado-imagenes.md).
- Entrenamiento y métricas: [ml-entrenamiento.md](ml-entrenamiento.md) y [ml-evaluacion.md](ml-evaluacion.md) (Día 5, pendientes).
