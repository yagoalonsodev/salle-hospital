# Diario IA — Sin patients.csv (2026-05-16)

| Campo | Valor |
|-------|-------|
| Herramienta | Cursor |
| Resultado | acierto |
| Spec | `docs/specs/pipeline-datos-ejemplo.md` |

### Prompt (optimizado)

```
Eliminar patients.csv falso; mantener studies/manifest; actualizar script y docs SDD/diario.
```

### Resumen

- Eliminado `data/raw/clinical/patients.csv`.
- `studies.csv` conserva `patient_id` opaco (1:1) para FK en Postgres.
- Sesión SDD: [salle-sdd/sessions/2026-05-16-sin-patients-csv.md](../../salle-sdd/sessions/2026-05-16-sin-patients-csv.md).
