# Dashboard Streamlit — laSalle Health

**Estructura del módulo:** [`docs/estructura-repositorio.md`](../docs/estructura-repositorio.md#dashboard--visualización-streamlit).

Visualización operativa (Día 7): métricas IA, imágenes, pipeline, alertas y calidad.

## Arranque

```bash
docker compose up -d --build postgres minio ml api dashboard
```

- **Dashboard:** http://localhost:8501
- **API:** http://localhost:8000

## Pestañas

| Pestaña | Contenido |
|---------|-----------|
| IA y clases | % predicciones producción, matriz confusión test |
| Imágenes | Galería estudios en MinIO |
| Logs | Resumen `pipeline_runs` + líneas en MongoDB (`GET /api/logs`) |
| Alertas | Tabla `alerts`, acuse de lectura |

Datos vía `GET /api/dashboard`.
