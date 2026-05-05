# Resultados — `rx_resnet50_v1` (Día 5)

**Evaluado:** 2026-05-16 · **Fuente:** `rx_resnet50_v1.h5` (fase 1 cabeza + fine-tuning 7 épocas, Metal M3)  
**Informe completo JSON:** `ml/models/reports/training_report_v1.json`  
**Resumen legible:** `ml/models/reports/metrics_summary.md`  
**Decisión de arquitectura:** `ml/notebooks/01_exploracion_arquitectura.ipynb` (sección informe)

## Entrenamiento

| Fase | Descripción | Épocas |
|------|-------------|--------|
| 1 | Backbone ResNet50 congelado, solo cabeza | 8 (CSV `training_log_phase1.csv`) |
| 2 | Fine-tuning últimas ~40 capas, LR 1e-5 | 7 (CSV `training_log_phase2.csv`) |

Mejor **val_accuracy** en fine-tune: **92,81 %** (época 3). Checkpoint: `rx_resnet50_v1_03_val0.9281.keras`.

> **Nota:** la exportación SavedModel falló en macOS (Python 3.12 + Keras `model.export`). El `.h5` y las métricas son válidos; ver `training_stdout_metal.log`.

## Artefactos

| Artefacto | Ruta |
|-----------|------|
| Modelo `.h5` | `ml/models/rx_resnet50_v1.h5` |
| SavedModel | `ml/models/savedmodel/rx_resnet50_v1/` (pendiente re-export) |
| Matrices de confusión | `confusion_matrix_{train,validation,test}.png` |
| Curvas | `training_curves.png` |
| Logs de épocas | `training_log_phase1.csv`, `training_log_phase2.csv` |

---

## TRAIN (n = 17 396)

| accuracy | precision (macro) | recall (macro) | F1 (macro) | F1 (weighted) |
|----------|-------------------|----------------|------------|---------------|
| **94,0 %** | 94,3 % | 91,7 % | 92,9 % | 93,9 % |

| clase | precision | recall | F1 | support |
|-------|-----------|--------|-----|---------|
| covid | 95,4 % | 92,8 % | 94,1 % | 1 564 |
| neumonia | 93,9 % | 97,6 % | 95,7 % | 11 540 |
| sana | 93,6 % | 84,7 % | 88,9 % | 4 292 |

---

## VALIDATION (n = 765)

| accuracy | precision (macro) | recall (macro) | F1 (macro) | F1 (weighted) |
|----------|-------------------|----------------|------------|---------------|
| **92,8 %** | 93,4 % | 89,3 % | 91,1 % | 92,8 % |

| clase | precision | recall | F1 | support |
|-------|-----------|--------|-----|---------|
| covid | 98,3 % | 83,8 % | 90,5 % | 68 |
| neumonia | 94,0 % | 95,7 % | 94,8 % | 508 |
| sana | 87,9 % | 88,4 % | 88,1 % | 189 |

---

## TEST (n = 1 285) — métricas para memoria / presentación

| accuracy | precision (macro) | recall (macro) | F1 (macro) | F1 (weighted) |
|----------|-------------------|----------------|------------|---------------|
| **94,0 %** | 93,7 % | 92,6 % | 93,1 % | 94,0 % |

| clase | precision | recall | F1 | support |
|-------|-----------|--------|-----|---------|
| covid | 97,2 % | 91,3 % | 94,2 % | 115 |
| neumonia | 96,0 % | 95,4 % | 95,7 % | 853 |
| sana | 87,8 % | 91,2 % | 89,5 % | 317 |

### Matriz de confusión (test)

|  | → covid | → neumonia | → sana |
|--|---------|------------|--------|
| **covid** | 105 | 7 | 3 |
| **neumonia** | 2 | 814 | **37** |
| **sana** | 1 | 27 | 289 |

**37 neumonías → sana** (FN críticos; antes del fine-tune: 154). Ver [`evaluacion-clinica-v1.md`](evaluacion-clinica-v1.md).

### Evolución respecto a solo fase 1 (cabecera)

| Métrica test | Solo fase 1 | Tras fine-tune |
|--------------|-------------|----------------|
| Accuracy | 81,9 % | **94,0 %** |
| F1 macro | 79,6 % | **93,1 %** |
| FN neumonía → sana | 154 | **37** |

---

## Reproducir métricas

```bash
docker compose run --rm --no-deps \
  -v ./data:/opt/data -v ./ml/models:/app/models \
  -e FEATURES_ROOT=/opt/data/processed/features \
  -e EVAL_BATCH_SIZE=4 \
  ml python scripts/export_all_metrics.py
```

Entrenamiento completo (fase 1 + fine-tune):

```bash
cd ml && source .venv-metal/bin/activate
export FEATURES_ROOT="../data/processed/features" FEATURES_VERSION=v1
export TRAIN_BATCH_SIZE=16 FINETUNE_EPOCHS=8
python scripts/train_resnet50.py          # fase 1
python scripts/finetune_from_checkpoint.py  # fase 2
```
