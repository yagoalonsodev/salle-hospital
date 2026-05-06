# Sesión SDD — Skills Diario IA y SDD (2026-05-01)

> Commit: `7fe54ab` — 2026-05-01 21:20  
> Ampliación convenciones (capas back/front): 2026-06 — documentado en skill SDD; aplicado en Día 6 (`api/`).

## Flujo aplicado

1. Crear `.cursor/skills/diario-ia/` y `.cursor/skills/salle-sdd/`
2. Plantillas, `AGENTS.md`, `docs/specs/BACKLOG.md`, `docs/diario-ia/`
3. Primera entrada diario: `docs/diario-ia/entradas/2026-05-01.md`

## Artefactos

| Artefacto | Ruta |
|-----------|------|
| Skill diario | `.cursor/skills/diario-ia/SKILL.md` |
| Skill SDD | `.cursor/skills/salle-sdd/SKILL.md` |
| Backlog inicial | `docs/specs/BACKLOG.md` |

## Convenciones que fijan los skills (SDD + Diario)

Estas reglas las debe seguir la IA en **todas** las sesiones posteriores; no son opcionales.

### 1. Spec antes de código

- Toda feature nueva → `docs/specs/<capa>-<nombre>.md` + entrada en `BACKLOG.md`.
- En la spec, separar explícitamente:
  - **Reglas de negocio** (qué debe ocurrir).
  - **Interfaz** (pantallas, endpoints, JSON).
  - **Infra** (BD, MinIO, servicios externos).

### 2. Un framework para la API REST

- Fachada hospitalaria: **solo Flask** en `api/`.
- Inferencia: microservicio **`ml/`** (FastAPI), llamado por HTTP — no duplicar endpoints públicos ahí.

### 3. Capas separadas — vista en vista, back en back

No mezclar responsabilidades entre carpetas:

```
Vista (front)     templates/ + static/     → HTML, CSS, JS, fetch JSON
Controlador       routes/                  → HTTP delgado, status codes
Aplicación        services/                → reglas de negocio y orquestación
Validación        validators.py            → formato/tamaño de inputs
Persistencia      db.py                    → PostgreSQL
Config            config.py + .env           → variables, sin lógica
```

**Prohibido:**

| En vista (`static/js`, templates) | En rutas (`routes/`) |
|-----------------------------------|----------------------|
| SQL, MinIO, ML | Reglas de negocio largas, queries |
| Reglas clínicas o de dominio | Orquestación completa del caso de uso |
| Secretos o URLs internas de Docker | Lógica duplicada que ya está en `services/` |

**Correcto:** el JS llama `POST /upload` y muestra el JSON; `services/pipeline.py` ejecuta subida → inferencia → guardado.

### 4. Diario IA alineado con capas

Al documentar una sesión, indicar **qué capa** se tocó (vista / routes / services / pipeline / ml), no mezclar «hice la API y el front» en un solo bloque sin distinguir archivos.

## Referencia implementación Día 6

| Capa | Ejemplo en repo |
|------|-----------------|
| Vista | `api/app/templates/index.html`, `static/js/app.js` |
| Controlador | `api/app/routes/upload.py` → delega en `pipeline` |
| Negocio | `api/app/services/pipeline.py` |
| Validación | `api/app/validators.py` |
| BD | `api/app/db.py` |
