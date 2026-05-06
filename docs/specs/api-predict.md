# Spec: API Flask + integración ML (Día 6)

| Meta | Valor |
|------|-------|
| Estado | implementado |
| Módulo | api, ml |
| BACKLOG | D6-01, D6-02, D6-03, D6-05 |

## Endpoints

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/` | Interfaz web (HTML/CSS/JS, 3 pestañas) |
| GET | `/health` | Estado API, PostgreSQL, MinIO, servicio ML |
| GET | `/metrics` | Contadores + radiografías API con predicción |
| POST | `/upload` | Subir RX → MinIO → inferencia → `predictions` |
| POST | `/predict` | Inferencia sobre archivo o `study_id` existente |
| GET | `/api/studies/<study_id>/image` | Servir imagen desde MinIO |

Ver también [api-pacientes.md](api-pacientes.md) para CRUD pacientes y `/api/sites`.

## Validación de imágenes

- Extensiones: `.jpg`, `.jpeg`, `.png`
- Tamaño máximo: 10 MB
- Comprobación magic bytes + PIL (`verify`, modo RGB)
- Dimensiones mínimas 64×64
- `patient_id` obligatorio en `/upload` (paciente debe existir)

## Flujo `/upload`

1. Validar archivo y `patient_id`
2. Generar `study_id` (hash del contenido)
3. Subir binario a MinIO `uploads/{study_id}.jpg`
4. Insertar estudio (`split=clinical`, `label=NULL`, `source_dataset=api_upload`)
5. Llamar microservicio ML `POST /predict`
6. Insertar fila en `predictions`

## Capas (`api/app/`)

| Capa | Ruta |
|------|------|
| Vista | `templates/`, `static/` |
| Rutas | `routes/` |
| Casos de uso | `services/pipeline.py`, `services/patients.py` |
| Persistencia | `db.py`, `repositories/` |
| Validación | `validators.py`, `validators_patients.py` |

## Criterios de aceptación

- [x] API Flask en puerto 8000 (Gunicorn `app.wsgi:app`)
- [x] Predicciones en PostgreSQL; imágenes en MinIO
- [x] Inferencia automática al subir
- [x] UI: galería por paciente y resumen con `study_id` + predicción
- [x] Microservicio ML FastAPI en `:8001` (solo interno)
