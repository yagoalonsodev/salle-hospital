---
name: salle-seguridad
description: >-
  Revisión de secretos y buenas prácticas de seguridad en salle-hospital.
  Usar antes de commits, al añadir servicios Docker, scripts con credenciales
  o cuando el usuario pida auditoría de seguridad, .env o secretos hardcodeados.
---

# Seguridad — salle-hospital

## Reglas obligatorias

1. **Nunca** commitear `.env`, claves API, tokens ni `*.pem`.
2. **Fuente de verdad:** `.env` (local, gitignored) copiado desde `.env.example`.
3. **En código Python:** usar `os.environ` / `scripts/env_utils.py` — **sin** contraseñas por defecto en `getenv(..., "secret")`.
4. **docker-compose:** valores por defecto `${VAR:-...}` solo para desarrollo local; documentar en `.env.example`.
5. **SQL init:** si el password está en `.sql`, debe coincidir con `.env.example` y llevar comentario; preferir variables de entorno en entrypoints futuros.
6. **README/docs:** no pegar contraseñas reales; enlazar a `.env.example` o «credenciales de desarrollo en `.env`».
7. **Commits:** no incluir `Co-authored-by: Cursor` ni trailers de agentes en mensajes de commit.

## Checklist pre-commit

```bash
# Secretos en código (debe devolver vacío salvo .env.example y compose defaults)
git grep -nE 'salle_secret|Admin123|minioadmin|airflow_secret' -- ':!.env.example' ':!docker-compose.yml' ':!*.md' ':!infra/postgres/*.sql'

# .env no trackeado
git check-ignore -v .env

# Trailers Cursor en último commit
git log -1 --format=%B | grep -i cursoragent && echo 'QUITAR Co-authored-by'
```

## Variables en `.env`

| Variable | Uso |
|----------|-----|
| `POSTGRES_USER` / `POSTGRES_PASSWORD` / `POSTGRES_DB` | App PostgreSQL |
| `AIRFLOW_DB_*` | Metadatos Airflow |
| `AIRFLOW_ADMIN_USER` / `AIRFLOW_ADMIN_PASSWORD` | UI Airflow |
| `MINIO_ROOT_USER` / `MINIO_ROOT_PASSWORD` | MinIO |
| `DATABASE_URL` | Cadena completa app (scripts, pipeline) |

## Si se filtró un secreto

1. Rotar credencial en `.env` y servicios.
2. `git rm --cached .env` si se añadió por error.
3. Si ya se pusheó: rotar + considerar `git filter-repo` (historial).

## Integración

- SDD: revisar spec por datos sensibles.
- Diario IA: no volcar secretos en entradas del diario.
