# Spec: Historial médico — radiografías e informes clínicos

| Meta | Valor |
|------|-------|
| Estado | hecho |
| Módulo | api |
| BACKLOG | D10-CL-03 |

## 1. Descripción funcional

En el detalle del paciente, mostrar **dos bloques separados**:

1. **Radiografías** — estudios RX + predicción ResNet50 (existente).
2. **Informes clínicos** — consultas por síntomas, diagnóstico de referencia (si importado) y predicción del modelo textual.

Nueva pestaña **Diagnóstico** para introducir síntomas y obtener predicción vía API Flask → ML.

## 2. Inputs

| Input | Tipo | Origen |
|-------|------|--------|
| `patient_id` | string | UI |
| `symptoms`, `age`, `sex` | JSON | Formulario diagnóstico |

## 3. Outputs

| Output | Tipo | Destino |
|--------|------|---------|
| `GET /api/patients/:id` | JSON | `studies[]` + `clinical_reports[]` |
| `POST /api/clinical/predict` | JSON | predicción + fila en `clinical_predictions` |

## 4. Restricciones

### Técnicas (SDD)

- Lógica en `services/clinical.py`, `repositories/clinical.py`.
- Rutas finas en `routes/clinical.py`.
- Front solo `fetch` en `static/js/clinical.js`.

### Negocio

- Paciente debe existir antes de guardar predicción.
- No confundir predicción RX (`predictions`) con clínica (`clinical_predictions`).

## 5. Criterios de aceptación

- [x] Detalle paciente con secciones RX e informes clínicos.
- [x] Pestaña Diagnóstico con formulario y resultado visual.
- [x] UI refinada (historial tipo informes, badges por enfermedad).

## 6. Prompt base para la IA

```text
En historial médico: radiografías y aparte diagnósticos como otros informes.
Integrar predicción por síntomas en el front y hacerlo más bonito.
```

## 7. Notas de implementación

- Migración: `infra/postgres/06-clinical-records.sql`
- JS: `clinical.js`; estilos en `style.css` (`.history-section`, `.diag-badge`).
