# Sesión SDD — 2026-05-05 · Informe comparativa arquitecturas (Día 5)

| Campo | Valor |
|-------|-------|
| Commit | `d3b3312` 2026-05-05 16:30 (+0200) |
| BACKLOG | D5-01, D5-02, D5-03 |
| Spec | `docs/specs/ml-entrenamiento.md` |
| Diario | `docs/diario-ia/entradas/2026-05-05.md` |

## Prompt único (contexto de la sesión)

Informe ejecutable en notebook alineado con `enunciado.md` (Día 5):

- Entrenar y evaluar **4 arquitecturas** con el mismo protocolo: `baseline_cnn`, `resnet50`, `efficientnetb0`, `densenet121`.
- Por cada una: entrenamiento → estadísticas test (accuracy, F1 macro, matriz, FN neumonía→sana).
- Comparativa final automática (`architecture_comparison.json`) + gráficos.
- **Conclusión honesta para memoria:** DenseNet121 gana F1 macro; ResNet50 sigue siendo modelo operativo (menor FN crítico, mejor accuracy, Docker).
- Añadir en notebook explicación pedagógica de **F1 macro**.
- Documentar en diario IA y cerrar SDD/backlog.

## Implementación

| Componente | Ruta |
|------------|------|
| Core entrenamiento | `ml/scripts/training_core.py` |
| Scripts por arquitectura | `ml/scripts/train_baseline_cnn.py`, `train_resnet50.py`, `train_efficientnetb0.py`, `train_densenet121.py` |
| Orquestación | `ml/scripts/train_compare_architectures.py` |
| Informe | `ml/notebooks/01_exploracion_arquitectura.ipynb` |
| Comparativa JSON | `ml/models/reports/architecture_comparison.json` |
| Resultados / clínica | `docs/ml/resultados-entrenamiento-v1.md`, `docs/ml/evaluacion-clinica-v1.md` |

## Métricas test (n=1285)

| Modelo | Accuracy | F1 macro | FN neumonía→sana |
|--------|----------|----------|------------------|
| densenet121 | 93,2 % | **93,4 %** | 72 |
| resnet50 | **94,0 %** | 93,1 % | **37** |
| baseline_cnn | 87,7 % | 87,8 % | 118 |
| efficientnetb0 | 66,4 % | 26,6 % | no usable |

Ranking script: F1 macro → **densenet121**. Producción: **resnet50** (`production_model` en JSON).

## Criterios encargo cubiertos

- Investigar arquitecturas (CNN propia + 3 preentrenados ImageNet).
- Matriz de confusión y reflexión clínica (por modelo + docs).
- No depender solo de accuracy (F1 macro + FN prioritario).
- Artefactos `.h5` (checkpoints ignorados en git); SavedModel pendiente en entorno local macOS.

## Limitaciones documentadas

- EfficientNetB0: colapso (predicción degenerada).
- `model.export` SavedModel falla en Python 3.12/macOS → `EXPORT_SAVEDMODEL=0` en notebook.
- ResNet50 ya entrenado antes; informe legacy `training_report_v1.json` integrado en comparativa.

## Siguiente

- D4-04: export SavedModel en Docker + servicio inferencia `ml`.
- Dashboard matriz de confusión (D7-01).
