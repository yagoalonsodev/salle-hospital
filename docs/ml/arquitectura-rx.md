# Arquitectura del modelo — clasificación de radiografías de tórax

**Proyecto:** salle-hospital (laSalle Health Center)  
**Fecha:** 2026-05-04 (Día 4)  
**Clases:** `sana` · `neumonia` · `covid`  
**Dataset:** `data/processed/features/v1/` (~6 399 fuentes → ~19 446 muestras con augmentation en train)

---

## 1. Problema y contexto

Se busca un clasificador multiclase sobre radiografías de tórax preprocesadas a **224×224** píxeles. El volumen de datos es **moderado** para deep learning puro (miles de imágenes, no millones), con posible **desbalance** entre clases (p. ej. menos COVID que neumonía en test). En este escenario, entrenar una CNN grande desde cero suele **subajustar** o converger lento; el **Transfer Learning** aprovecha representaciones aprendidas en ImageNet y se adapta al dominio médico con menos datos y menos tiempo.

---

## 2. CNN propia vs Transfer Learning

| Criterio | CNN propia (baseline) | Transfer Learning |
|----------|----------------------|-------------------|
| Datos necesarios | Muchos (decenas de miles+) | Pocos–moderados |
| Tiempo de entrenamiento | Alto para buena accuracy | Menor |
| Accuracy esperada (RX, 3 clases) | Baja–media | Media–alta |
| Interpretabilidad / simplicidad | Alta (pocas capas) | Media |
| Alineación con encargo | Útil como **comparación** | **Recomendado** como modelo final |
| Parámetros (nuestro baseline) | ~0,4M | ResNet50 ~24M (mayoría congelables al inicio) |

**Conclusión:** se adopta **Transfer Learning** como enfoque principal. La CNN propia (`baseline_cnn` en `ml/models/architectures.py`) se mantiene como **línea base** en el notebook para contrastar complejidad y capacidad.

---

## 3. Comparativa de backbones (Transfer Learning)

| Modelo | Parámetros (aprox.) | Input | Ventajas | Inconvenientes |
|--------|---------------------|-------|----------|----------------|
| **ResNet50** | ~23,6M | 224×224 | Muy usado en imágenes médicas; API Keras madura; buen equilibrio calidad/tiempo | No es el más ligero |
| **EfficientNetB0** | ~5,3M | 224×224 | Eficiente; buen accuracy por parámetro | Ajuste de LR más sensible |
| **DenseNet121** | ~8,0M | 224×224 | Reutilización de features; citado en literatura RX | Más coste de memoria en batch grandes |

### ResNet50

Arquitectura residual que mitiga el desvanecimiento del gradiente en redes profundas. En clasificación de neumonía/COVID en RX aparece de forma recurrente en trabajos académicos y competiciones Kaggle. Pesos ImageNet (`imagenet`) proporcionan filtros de bordes, texturas y formas reutilizables en patrones pulmonares.

### EfficientNetB0

Escala profundidad, ancho y resolución de forma compuesta. Interesante si se prioriza inferencia rápida en Docker; en este proyecto la prioridad es **reproducibilidad y documentación**, no el mínimo latencia.

### DenseNet121

Conexiones densas entre capas; buen rendimiento en algunos benchmarks médicos. Se descarta como modelo **principal** por menor margen de mejora frente a ResNet50 en un plazo de práctica acotado, sin aportar una ventaja clara frente al coste de explicación.

---

## 4. Decisión final

| Elemento | Elección |
|----------|----------|
| Enfoque | **Transfer Learning** |
| Backbone | **ResNet50** (`tensorflow.keras.applications.ResNet50`) |
| Cabeza | `GlobalAveragePooling2D` → `Dropout(0.4)` → `Dense(3, softmax)` |
| Entrada | 224×224×3, `Rescaling(1/255)` |
| Entrenamiento (Día 5) | Fase 1: backbone congelado; Fase 2: fine-tuning últimas capas |
| Export | **SavedModel** (servicio FastAPI) + checkpoint **`.h5`** si se requiere en memoria |

### Por qué ResNet50 y no EfficientNetB0

1. **Menor riesgo de implementación** en el equipo (más ejemplos, más issues resueltos en Stack Overflow / Keras).
2. **Alineación con el plan del encargo** (recomendación explícita ResNet50).
3. **224×224** coincide con el preprocesado Spark sin cambiar resolución.
4. EfficientNetB0 queda documentado como **alternativa viable** si en Día 5 el tiempo de entrenamiento fuera excesivo.

### Por qué no solo CNN propia

Con ~6 400 imágenes fuente (aunque ~19 k tras augmentation), una CNN shallow no alcanza típicamente la misma generalización que un backbone ImageNet, sobre todo en la frontera **neumonía vs COVID-19** (patrones superpuestos).

---

## 5. Implicaciones para el Día 5 (entrenamiento)

| Entregable encargo | Implementación prevista |
|--------------------|-------------------------|
| Entrenar modelo | `ml/scripts/train_resnet50.py` (o notebook `02_entrenamiento.ipynb`) |
| Checkpoints | `ml/models/checkpoints/` |
| Métricas | accuracy, precision, recall, F1 (por clase y macro) |
| Matriz de confusión | `ml/models/reports/confusion_matrix.png` |
| Curvas | `history.png` (loss / accuracy train vs val) |
| Modelo `.h5` | `ml/models/rx_resnet50_v1.h5` |
| Servicio | SavedModel en `ml/models/savedmodel/rx_resnet50_v1/` |

### Falsos positivos y negativos (marco clínico, a desarrollar con métricas)

| Error | Ejemplo | Impacto clínico |
|-------|---------|-----------------|
| **Falso positivo** (predice enfermedad, paciente sano) | RX sana clasificada como neumonía | Pruebas adicionales, ansiedad, sobrecarga del sistema |
| **Falso negativo** (predice sano, hay patología) | Neumonía clasificada como sana | Retraso en tratamiento; **riesgo mayor** que un FP en screening |
| Confusión **COVID ↔ neumonía** | Patología A etiquetada como B | Aislamiento o protocolo incorrecto; requiere confirmación PCR/imagen experta |

El sistema se plantea como **soporte a la decisión**, no sustituto del radiólogo. Las métricas del Día 5 deben revisarse **por clase** (no solo accuracy global) por el desbalance.

---

## 6. Referencias de implementación

- Spec SDD: [`docs/specs/ml-arquitectura.md`](../specs/ml-arquitectura.md)
- Código: [`ml/models/architectures.py`](../../ml/models/architectures.py)
- Notebook: [`ml/notebooks/01_exploracion_arquitectura.ipynb`](../../ml/notebooks/01_exploracion_arquitectura.ipynb)
- Preprocesado: [`docs/specs/pipeline-preprocesado-imagenes.md`](../specs/pipeline-preprocesado-imagenes.md)
