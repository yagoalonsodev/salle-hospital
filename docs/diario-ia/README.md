# Diario de desarrollo con IA

Entregable obligatorio (`enunciado.md`): documentar herramientas, prompts, aciertos, correcciones y reflexión crítica.

## Herramienta principal

**Cursor** — desarrollo asistido por IA (Vibe Coding).

## Cómo se guarda cada entrada

1. Trabajas con Cursor en el proyecto.
2. Al terminar una interacción relevante, el agente (skill `@diario-ia`) **pregunta** si quieres guardarla.
3. Si aceptas, se añade a `entradas/YYYY-MM-DD.md` y se actualiza [`INDEX.md`](INDEX.md).

Puedes decir en cualquier momento: *«guárdalo en el diario»* o *«no guardes esto»*.

## Estructura

```
docs/diario-ia/
├── README.md          ← este archivo
├── INDEX.md           ← índice de entradas
└── entradas/
    └── YYYY-MM-DD.md  ← un archivo por día
```

## Qué incluye cada entrada

- Prompt del usuario (literal o fiel)
- Resumen de la respuesta de la IA
- Resultado: acierto / parcial / corrección
- Si hubo corrección: qué falló y cómo se arregló
- Archivos tocados y spec SDD relacionada
- Reflexión breve

Plantilla: `.cursor/skills/diario-ia/entry-template.md`

## Uso en Cursor

Menciona `@diario-ia` o pide *«usa el diario IA»*. Para planificar código con specs: `@salle-sdd`.
