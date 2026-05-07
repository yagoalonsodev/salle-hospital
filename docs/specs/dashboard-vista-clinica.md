# Spec: Dashboard Streamlit + robustez operativa (Día 7)

| Meta | Valor |
|------|-------|
| Estado | implementado |
| Módulo | dashboard, api |
| BACKLOG | D7-01, D7-02, D7-03, D7-04 |

## 1. Descripción funcional

Dashboard **Streamlit** (`:8501`) que consume la API Flask (`:8000`) y muestra:

- Métricas IA (predicciones, % por clase, evaluación test del modelo)
- Imágenes procesadas (subidas API con miniatura)
- Alertas (tabla `alerts` + salud degradada)
- Estado del pipeline (`pipeline_runs`, eventos recientes)
- Errores de calidad (`data_quality_issues`)

Robustez: logging centralizado en API, reintentos HTTP al ML, alertas automáticas en fallos de inferencia/pipeline.

## 2. Endpoints API (nuevos)

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/api/dashboard` | Payload agregado para Streamlit |
| PATCH | `/api/alerts/<id>/ack` | Marcar alerta como leída |

## 3. Criterios de aceptación

- [x] Dashboard usable en http://localhost:8501
- [x] Gráficas: torta % por clase, matriz de confusión (test)
- [x] Listado imágenes con `study_id` y predicción
- [x] Alertas visibles (BD + inferencia/pipeline)
- [x] Estado pipeline (últimas ejecuciones)
- [x] Logging estructurado en API
- [x] Retry automático llamadas ML (3 intentos)
- [x] Healthchecks Docker API y dashboard

## 4. Prompt base

```text
Implementar dashboard Streamlit Día 7: métricas IA, imágenes, alertas, pipeline,
gráficas % clase y errores; robustez con logging, retry ML y alertas en fallos.
```
