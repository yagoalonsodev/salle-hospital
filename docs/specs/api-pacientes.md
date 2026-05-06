# Spec: API pacientes y estudios (Día 6)

| Meta | Valor |
|------|-------|
| Estado | implementado |
| Módulo | api |
| BACKLOG | D6-04 |

## Endpoints

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/api/patients` | Listar pacientes con conteo de RX |
| POST | `/api/patients` | Crear paciente (`display_name`, sex, age_range, site_code) |
| GET | `/api/patients/<id>` | Detalle + estudios con última predicción |
| PUT/PATCH | `/api/patients/<id>` | Actualizar |
| DELETE | `/api/patients/<id>` | Eliminar (`?cascade_studies=true`) |
| GET | `/api/sites` | Catálogo de centros (`sites`) |
| GET | `/api/studies/<id>/image` | Imagen RX desde MinIO |

## Modelo de datos

- `patients.display_name` — nombre visible en UI (simulado, sin DNI).
- `patients.site_code` → FK `sites`.
- `studies.label` — NULL en subidas API (ground truth solo en ingesta batch).
- `studies.split` — `clinical` para `source_dataset=api_upload`.

## UI web (vista)

- Pestaña **Pacientes**: CRUD, detalle, lista de RX por fecha.
- Pestaña **Radiografías**: selector paciente, subida, galería MinIO + predicción.
- Pestaña **Resumen**: métricas + listado `study_id` + predicción.

## Criterios de aceptación

- [x] Paciente con 0..N radiografías
- [x] Subida exige paciente existente
- [x] Centros desde tabla `sites`, sin valores hardcodeados en formulario
- [x] Galería y resumen muestran predicción persistida en `predictions`
