---
name: diario-ia
description: >-
  Gestiona el Diario de desarrollo con IA (entregable obligatorio de la práctica).
  Tras cada interacción sustantiva, pregunta si guardar prompt, respuesta y correcciones
  en docs/diario-ia/. Usar cuando el usuario mencione diario IA, vibe coding, prompts,
  documentar IA, o al cerrar tareas de desarrollo con asistencia de Cursor.
---

# Diario IA — laSalle Health Center

## Objetivo

Documentar el uso de IA (Cursor) según `enunciado.md`: prompts, resultados, correcciones e iteraciones. Es un **entregable obligatorio** de la memoria técnica.

## Cuándo activar el flujo

Al terminar una respuesta **sustantiva** (código, infra, diseño, debugging, specs), **antes de cerrar**:

1. Usa **AskQuestion** (si está disponible) con:

   - **Pregunta:** `¿Quieres guardar esta interacción en el Diario IA?`
   - **Opciones:**
     - `Sí, guardar`
     - `No, ahora no`
     - `Sí, pero quiero editar antes`

2. Si AskQuestion no está disponible, pregunta lo mismo en texto al final del mensaje.

3. **No guardes sin confirmación explícita** del usuario (salvo que diga «guárdalo en el diario» en el mismo mensaje).

## Dónde guardar

| Recurso | Ruta |
|---------|------|
| Entradas del día | `docs/diario-ia/entradas/YYYY-MM-DD.md` |
| Plantilla de entrada | [entry-template.md](entry-template.md) |
| Índice global | `docs/diario-ia/INDEX.md` |

- Un archivo por **día** (`YYYY-MM-DD.md`); varias entradas separadas por `---`.
- ID de entrada: `### Entrada NNN — título corto` (NNN = 001, 002… por día).
- Tras guardar, actualiza `docs/diario-ia/INDEX.md` (fecha, título, enlace al ancla).

## Contenido mínimo de cada entrada

Copia la plantilla de [entry-template.md](entry-template.md). Campos obligatorios:

- **Herramienta:** Cursor (modelo si se conoce)
- **Prompt del usuario** (texto literal o resumen fiel)
- **Respuesta de la IA** (resumen de lo hecho, no pegar todo el chat)
- **Resultado:** `acierto` | `parcial` | `corrección`
- **Corrección** (si aplica): qué estaba mal, prompt de corrección, solución final
- **Archivos afectados** (rutas)
- **Spec SDD** (si existe): enlace a `docs/specs/…`
- **Reflexión** (1–3 frases): qué aportó la IA, limitaciones

## Si el usuario elige «editar antes»

Muestra el borrador en markdown y pide cambios. Solo escribe el archivo cuando confirme.

## Entrada inicial de ejemplo

Ver `docs/diario-ia/entradas/2026-05-01.md` como referencia de formato.

## Relación con SDD

Si la interacción implementó una spec, enlaza `docs/specs/<nombre>.md` y actualiza el estado en `docs/specs/BACKLOG.md` (skill `salle-sdd`).
