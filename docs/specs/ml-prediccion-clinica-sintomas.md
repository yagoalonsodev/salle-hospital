# Spec: ML predicción de enfermedad por síntomas

| Meta | Valor |
|------|-------|
| Estado | hecho |
| Módulo | ml |
| BACKLOG | D10-CL-02 |

## 1. Descripción funcional

Entrenar un clasificador **tabular + texto** (scikit-learn) que, a partir de síntomas, edad y sexo, predice la enfermedad. Modelo **distinto** de ResNet50 (radiografías). Servicio FastAPI expone `POST /predict-clinical`.

## 2. Inputs

| Input | Tipo | Origen |
|-------|------|--------|
| `records.csv` | CSV | `data/raw/clinical_records/` |
| `age`, `sex`, `symptoms` | JSON | API en inferencia |

## 3. Outputs

| Output | Tipo | Destino |
|--------|------|---------|
| `clinical_symptoms_v1.joblib` | modelo | `ml/models/` |
| `clinical_training_report_v1.json` | métricas | `ml/models/reports/` |
| Predicción JSON | API | probabilidades por clase |

## 4. Restricciones

### Técnicas

- scikit-learn + joblib (ya en `ml/requirements.txt`).
- Split 80/10/10 estratificado; métrica principal F1 macro.
- Umbral mínimo F1 macro ≥ 0.75 en validación (dataset sintético).

### Negocio

- Mismas 8 clases que el CSV de entrenamiento.
- Disclaimer: soporte a la decisión, no diagnóstico definitivo.

## 5. Criterios de aceptación

- [x] Script `ml/scripts/train_clinical_symptoms.py` entrena y guarda artefacto.
- [x] `POST /predict-clinical` en servicio `ml`.
- [x] Health incluye `clinical_model_loaded`.

## 6. Prompt base para la IA

```text
Entrenar modelo capaz de predecir enfermedades a partir de síntomas (dataset textual 100k).
```

## 7. Notas de implementación

- `ml/app/clinical_inference.py` — carga joblib e inferencia.
- Variables de entorno: `CLINICAL_MODEL_PATH`, `CLINICAL_MODEL_VERSION`.
