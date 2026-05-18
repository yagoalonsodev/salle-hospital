# Spec: reentrenamiento nocturno ResNet50 (Airflow)

| Meta | Valor |
|------|-------|
| Estado | implementado |
| Módulo | airflow, ml, pipeline |
| BACKLOG | D8A-04 |

## Descripción

DAG `salle_nightly_retrain` que, **cada día a la 01:00** (hora del scheduler Airflow), regenera features con PySpark a partir de `data/raw/` (imágenes antiguas + nuevas del watcher) y reentrena `rx_resnet50_v1`. Tras el entrenamiento reinicia `salle-ml` para cargar el `.h5` nuevo.

No sustituye la inferencia en tiempo real al subir RX por la UI; es un **reentrenamiento batch** opcional.

## Flujo

1. `check_retrain_enabled` — ShortCircuit si `NIGHTLY_RETRAIN_ENABLED=false`
2. `check_features_source` — comprueba que exista `data/raw/covid19_vs_pneumonia`
3. `spark_preprocess` — `preprocess_images.py` (Spark)
4. `train_resnet50` — `train_resnet50.py` en `salle-ml`
5. `reload_ml_service` — `docker restart salle-ml`

## Variables de entorno

| Variable | Default | Uso |
|----------|---------|-----|
| `NIGHTLY_RETRAIN_ENABLED` | `true` | Activar DAG lógicamente |
| `NIGHTLY_HEAD_EPOCHS` | `5` | Épocas fase cabeza (menor que entrenamiento manual) |
| `NIGHTLY_FINETUNE_EPOCHS` | `3` | Épocas fine-tuning |
| `FEATURES_ROOT` | `/opt/data/processed/features` | Dataset en contenedores |

## Criterios de aceptación

- [x] DAG programado `0 1 * * *`
- [x] Usa datos acumulados en `raw/` tras watcher + ingesta
- [x] Fallos generan alerta vía `airflow_callbacks`
- [x] Documentado en `airflow/README.md`

## Limitaciones

- Entrenamiento pesado (CPU/GPU); en Docker Desktop puede tardar horas.
- Hora 01:00 = zona horaria del scheduler Airflow (por defecto UTC salvo configuración).
