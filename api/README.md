# API Flask — laSalle Health Center

## Arranque (Docker)

```bash
docker compose up -d --build postgres minio ml api
```

- **Web UI:** http://localhost:8000/
- **Health:** http://localhost:8000/health
- **Métricas:** http://localhost:8000/metrics

Requisito: modelo `ml/models/rx_resnet50_v1.h5` montado en el contenedor `ml`.

## Endpoints

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/` | Interfaz de subida de radiografías |
| GET | `/health` | Estado de API, PostgreSQL, MinIO y ML |
| GET | `/metrics` | Contadores y últimas predicciones |
| POST | `/upload` | Subir RX → inferencia → guardar en BD |
| POST | `/predict` | Igual que upload o inferir por `study_id` |

## Ejemplo curl

```bash
curl -X POST http://localhost:8000/upload \
  -F "file=@/ruta/a/radiografia.jpg"
```

## Validaciones

- Solo `.jpg`, `.jpeg`, `.png` (magic bytes + PIL)
- Máximo 10 MB
- `patient_id` opcional: `PAT-` + 6–12 caracteres alfanuméricos
