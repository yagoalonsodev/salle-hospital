# Evaluación clínica — errores del clasificador RX (v1)

**Modelo:** ResNet50 + Transfer Learning (`rx_resnet50_v1`)  
**Entrenamiento:** fase 1 (cabeza) + fine-tuning 7 épocas · evaluado 2026-05-16  
**Clases:** `covid` · `neumonia` · `sana`  
**Métricas detalladas:** `ml/models/reports/training_report_v1.json`  
**Matriz de confusión:** generada en notebook `ml/notebooks/01_exploracion_arquitectura.ipynb` o `confusion_matrix_test.png` en reports

> El encargo **no exige un % de accuracy mínimo**. Valora la **interpretación** de errores y su impacto sanitario.

---

## 1. Formato del modelo (requisito vs. plan diario)

| Fuente | Qué pide |
|--------|----------|
| **Enunciado oficial** | Modelo en Docker, evaluación (matriz de confusión, reflexión clínica, métricas en memoria). **No menciona `.pt` ni `.h5`.** |
| **Arquitectura del proyecto** | **TensorFlow** → export **SavedModel** (servicio `ml`) + **`.h5`** (Keras, memoria/backup). |
| **Plan día a día** (`.pt` o `.h5`) | Formato genérico; **`.pt` = PyTorch**, incompatible con nuestro stack sin reescribir todo el módulo `ml/`. |

**Entregable adoptado:** `ml/models/rx_resnet50_v1.h5` (+ SavedModel en Docker cuando se re-exporte).

---

## 2. Falsos positivos (FP)

**Definición:** el modelo predice **patología** cuando el paciente está **sano** (o predice una enfermedad distinta a la real).

| Error | Ejemplo | Impacto clínico |
|-------|---------|-----------------|
| FP **sana → neumonía** | RX normal marcada como infección | Antibióticos innecesarios, ingreso evitable, ansiedad, coste |
| FP **sana → covid** | RX normal marcada como COVID | Aislamiento, PCR extra, saturación de camas |
| FP **neumonía → covid** | Neumonía bacteriana etiquetada como COVID | Protocolo de aislamiento incorrecto |

En screening, un FP suele generar **sobrediagnóstico** y pruebas de confirmación, pero rara vez retrasa un tratamiento urgente si el paciente estaba sano.

---

## 3. Falsos negativos (FN)

**Definición:** el modelo predice **sano** (o otra clase menos grave) cuando hay **patología real**.

| Error | Ejemplo | Impacto clínico |
|-------|---------|-----------------|
| FN **neumonía → sana** | Consolidación no detectada | Retraso en antibiótico; empeoramiento, especialmente en mayores |
| FN **covid → sana** | Opacidades COVID no vistas | Riesgo de contagio no aislado; propagación nosocomial |
| FN **covid → neumonía** | Confusión entre patologías similares | Tratamiento o aislamiento subóptimo |

Los **FN suelen ser más graves** que los FP en triaje: se pierde una ventana terapéutica o de contención.

---

## 4. Confusiones entre clases patológicas

Las RX de **neumonía** y **COVID-19** comparten opacidades en lóbulos; el modelo puede confundirlas aunque acierte “hay enfermedad”.

- **Impacto:** protocolo de aislamiento o antivírico distinto; siempre requiere **confirmación clínica/laboratorio**.
- **Mitigación:** no usar la salida del modelo como diagnóstico único; umbral de confianza y revisión radiológica.

---

## 5. Desbalance de clases

En test hay muchas más muestras de **neumonía** (853) que de **covid** (115). La **accuracy global** (~94 %) puede ocultar fallos en minorías si no se revisan recall y F1 por clase.

| Clase (test) | Recall | F1 | Comentario |
|--------------|--------|-----|------------|
| covid | 91,3 % | 94,2 % | Aceptable; 10 FN de 115 |
| neumonia | 95,4 % | 95,7 % | Clase mayoritaria, bien cubierta |
| sana | 91,2 % | 89,5 % | Más FP hacia neumonía (27) que hacia covid (1) |

---

## 6. Rol del sistema en el hospital (laSalle)

Este módulo es **soporte a la decisión**, no sustituto del radiólogo:

1. Priorizar estudios para revisión humana.  
2. Alertar sobre patrones sugestivos.  
3. Integrarse con PostgreSQL / dashboard sin automatizar tratamiento.

Cualquier despliegue real exigiría validación prospectiva, trazabilidad y cumplimiento RGPD/LOPDGDD.

---

## 7. Limitaciones (v1)

- Dataset público (sesgo de fuente, equipos, calidad variable).  
- Augmentation agresiva en train puede no reflejar RX clínica real.  
- Sin calibración de probabilidades ni explicabilidad (Grad-CAM, etc.) en esta versión.  
- Posible **sobreajuste** en train (94,0 %) respecto a validación (92,8 %); monitorizar en producción.

---

## 8. Resultados v1 (test, 1 285 RX)

| Métrica | Solo fase 1 (cabecera) | Tras fine-tune (v1 final) |
|---------|------------------------|---------------------------|
| Accuracy | 81,9 % | **94,0 %** |
| F1 macro | 79,6 % | **93,1 %** |
| Recall macro | 81,5 % | **92,6 %** |

### Matriz de confusión (test)

|  | → covid | → neumonia | → sana |
|--|---------|------------|--------|
| **covid** | 105 | 7 | 3 |
| **neumonia** | 2 | 814 | **37** |
| **sana** | 1 | 27 | 289 |

### Errores destacados

| Tipo | Conteo | Interpretación |
|------|--------|----------------|
| FN neumonía → sana | **37** | Sigue siendo el error más grave; mejoró respecto a fase 1 (**154**) |
| FP sana → neumonía | 27 | Sobrediagnóstico; menor que antes (32) |
| FP sana → covid | 1 | Aislamiento innecesario; muy reducido (antes 5) |
| FN covid (no acierto covid) | 10 (7+3) | Posible retraso de protocolo COVID; antes 28 |
| Confusión neumonía → covid | 2 | Patologías similares en imagen |
| Confusión covid → neumonía | 7 | Idem |

### Lectura clínica

1. **El fine-tune redujo de forma marcada los FN neumonía→sana**, el escenario de mayor riesgo en triaje, pero **37 casos** siguen siendo inaceptables para uso autónomo.  
2. **COVID** tiene buen recall (91,3 %); los errores restantes exigen PCR o revisión experta.  
3. **Sanos** se clasifican bien (recall 91,2 %); la mayoría de FP van a neumonía, no a covid.  
4. El sistema es adecuado como **priorizador / segunda lectura**, no como diagnóstico cerrado.

Detalle numérico: [`resultados-entrenamiento-v1.md`](resultados-entrenamiento-v1.md) y `ml/models/reports/training_report_v1.json`.
