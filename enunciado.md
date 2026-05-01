# Sistema Inteligente de Soporte Hospitalario

> Práctica integrada — Inteligencia Artificial, Big Data y desarrollo asistido por IA en un entorno sanitario simulado.

---

## Índice

1. [Contexto del proyecto](#contexto-del-proyecto)
2. [Objetivo del encargo](#objetivo-del-encargo)
3. [Alcance tecnológico](#alcance-tecnológico)
   - [Modelo de Inteligencia Artificial](#modelo-de-inteligencia-artificial)
   - [Procesamiento de datos / Big Data](#procesamiento-de-datos--big-data)
   - [Automatización de procesos](#automatización-de-procesos)
   - [Visualización y comunicación de resultados](#visualización-y-comunicación-de-resultados)
4. [Infraestructura y Sistemas de Big Data Aplicados](#infraestructura-y-sistemas-de-big-data-aplicados)
   - [Containerización y despliegue](#containerización-y-despliegue)
   - [Pipeline de datos a escala](#pipeline-de-datos-a-escala)
   - [Monitorización y calidad de datos](#monitorización-y-calidad-de-datos)
5. [Desarrollo Asistido por IA (Vibe Coding)](#desarrollo-asistido-por-ia-vibe-coding)
6. [Aprendizaje Automático: Clasificación de Radiografías](#aprendizaje-automático-y-redes-neuronales-clasificación-de-radiografías)
7. [Consideraciones éticas y legales](#consideraciones-éticas-y-legales)
8. [Enfoque del proyecto](#enfoque-del-proyecto)
9. [Entregables](#entregables)

---

## Contexto del proyecto

El hospital **laSalle Health Center**, una organización sanitaria de tamaño medio en proceso de transformación digital, ha detectado diversas ineficiencias en la gestión de sus datos clínicos y operativos.

Actualmente, el hospital dispone de grandes volúmenes de datos generados diariamente (historiales clínicos, registros de pacientes, pruebas diagnósticas, logs de sistemas, etc.), pero **no cuenta con herramientas avanzadas** que permitan:

- Extraer conocimiento útil a partir de estos datos
- Detectar patrones clínicos relevantes
- Automatizar procesos internos
- Apoyar la toma de decisiones médicas y operativas

Ante esta situación, el hospital ha contratado a vuestro equipo como **consultora tecnológica especializada en Inteligencia Artificial y Big Data**.

---

## Objetivo del encargo

El objetivo del proyecto es diseñar e implementar una solución informática basada en Inteligencia Artificial que permita:

- Analizar datos clínicos y/o operativos
- Identificar patrones, anomalías o clasificaciones relevantes
- Automatizar tareas repetitivas dentro del sistema
- Generar información útil para la toma de decisiones

La solución deberá simular un **sistema real de soporte hospitalario**, aportando valor en un entorno sanitario.

---

## Alcance tecnológico

La solución desarrollada deberá integrar, como mínimo, los siguientes componentes. Cada sección indica la asignatura y el profesor responsable de su evaluación.

### Modelo de Inteligencia Artificial

Se deberá implementar un modelo de IA que permita resolver un problema concreto, como, por ejemplo:

- Clasificación de pacientes
- Predicción de enfermedades
- Segmentación de perfiles clínicos

El modelo deberá estar **justificado** en función del problema planteado.

### Procesamiento de datos / Big Data

El sistema deberá trabajar con datos que presenten al menos una de las siguientes características:

- Volumen elevado
- Datos no estructurados (ej.: imágenes médicas)
- Integración de múltiples fuentes de datos

Se deberá diseñar un **flujo de tratamiento de datos (pipeline)**, incluyendo:

| Fase | Descripción |
|------|-------------|
| Ingesta | Incorporación de nuevos datos al sistema |
| Limpieza | Corrección y normalización |
| Transformación | Preparación para análisis |
| Análisis | Extracción de conocimiento |

### Automatización de procesos

El sistema deberá incluir mecanismos de automatización que mejoren la eficiencia operativa del hospital.

**Ejemplos:**

- Generación automática de informes
- Envío de alertas ante eventos relevantes
- Procesamiento automático de nuevos datos
- Organización o movimiento de ficheros

### Visualización y comunicación de resultados

Se deberán presentar los resultados de forma clara mediante:

- Gráficos
- Dashboards
- Informes interpretables

---

## Infraestructura y Sistemas de Big Data Aplicados

El proyecto deberá demostrar la capacidad de diseñar, desplegar y operar una infraestructura de datos que simule un entorno hospitalario real. **No basta con procesar datos localmente**: se requiere una arquitectura que refleje los principios de los sistemas de Big Data.

### Containerización y despliegue

Toda la infraestructura del proyecto deberá estar **containerizada** utilizando Docker y orquestada mediante Docker Compose (o similar). El objetivo es que **cualquiera pueda levantar el sistema completo con un solo comando**.

**Se valorará:**

- Definición clara de servicios (base de datos, procesamiento, API, dashboard, etc.)
- Separación de responsabilidades entre contenedores
- Uso de volúmenes para persistencia de datos
- Variables de entorno y configuración externalizada
- Documentación del despliegue (README con instrucciones paso a paso)

### Pipeline de datos a escala

Se deberá implementar un pipeline de datos completo que cubra las fases de **ingesta, almacenamiento, procesamiento y servicio**. El pipeline debe estar diseñado para poder escalar, aunque en el proyecto se trabaje con un volumen simulado.

**Requisitos mínimos:**

| Fase | Requisito |
|------|-----------|
| **Ingesta** | Mecanismo automatizado para incorporar nuevos datos (CSV, imágenes, APIs simuladas, etc.) |
| **Almacenamiento** | Uso combinado de al menos dos tipos (ej.: PostgreSQL para datos estructurados + MinIO/S3 o MongoDB para no estructurados) |
| **Procesamiento** | Al menos un framework escalable (Apache Spark/PySpark, Dask o Apache Beam), con justificación de la elección |
| **Servicio** | Datos procesados disponibles para consumo (API REST, conexión a dashboard, etc.) |

### Monitorización y calidad de datos

El sistema deberá incluir mecanismos básicos de:

- **Logging centralizado** de los procesos del pipeline
- **Validación de calidad** de datos (registros incompletos, duplicados o corruptos)
- **Alertas o notificaciones** ante fallos en el procesamiento (log, email simulado o entrada en el dashboard)

---

## Desarrollo Asistido por IA (Vibe Coding)

En el contexto profesional actual, el desarrollo de software está evolucionando rápidamente gracias a las herramientas de IA generativa. Este proyecto requiere que se adopten **activamente** estas herramientas como parte integral del flujo de trabajo, no como un complemento opcional.

### Uso obligatorio de herramientas de IA para el desarrollo

Se deberá utilizar **al menos una** herramienta de desarrollo asistido por IA durante el proyecto.

**Ejemplos de herramientas aceptadas:**

| Herramienta |
|-------------|
| Claude Code |
| GitHub Copilot |
| Windsurf |
| Antigravity |
| Codex de OpenAI |
| Google AI Studio con Gemini |
| Cursor |

### Metodología Spec-Driven Development (SDD)

El desarrollo del proyecto deberá seguir, al menos parcialmente, una metodología de **Spec-Driven Development (SDD)**. Esto significa que, antes de escribir código (o de pedirle a la IA que lo genere), se deberá redactar una especificación clara de lo que se quiere construir.

La especificación deberá incluir, como mínimo:

- Descripción funcional del componente o módulo
- Inputs y outputs esperados
- Restricciones técnicas y de negocio
- Criterios de aceptación

Esta especificación servirá como **prompt base** para la herramienta de IA y deberá entregarse como parte de la documentación del proyecto.

### Documentación del proceso de desarrollo con IA

Se deberá entregar un **diario de desarrollo con IA** que documente cómo se ha utilizado la herramienta a lo largo del proyecto. Este diario es un entregable obligatorio y debe incluir:

- Herramientas utilizadas y justificación de la elección
- Ejemplos representativos de prompts utilizados y su resultado
- Casos donde la IA acertó y casos donde hubo que corregir o iterar
- Reflexión crítica: qué aportó la IA al proceso, qué limitaciones se encontraron y cómo se superaron
- Estimación del impacto en productividad (tiempo ahorrado, calidad del código generado, etc.)

---

## Aprendizaje Automático y Redes Neuronales: Clasificación de Radiografías

En este bloque, el equipo deberá diseñar y desarrollar un **módulo de Deep Learning** orientado al análisis de imágenes médicas. El propósito no es solo obtener un código funcional, sino demostrar autonomía e iniciativa para investigar y justificar la solución técnica más adecuada para el hospital.

### El reto: Clasificación triple

El sistema debe ser capaz de procesar radiografías de tórax para clasificar a los pacientes en **tres categorías**:

| Categoría | Descripción |
|-----------|-------------|
| **Sana** | Sin patologías detectables |
| **Neumonía** | Presencia de infección bacteriana o viral estándar |
| **COVID-19** | Patrones específicos asociados a esta patología |

### Investigación y desarrollo

A diferencia de otros módulos, aquí el equipo tiene **libertad para investigar** y decidir cómo abordar el problema. Se valorará la capacidad de búsqueda de soluciones utilizando herramientas de IA. Deberéis documentar:

1. **Elección del modelo** — Investigar y decidir qué arquitectura es la más eficiente (redes convolucionales, modelos preentrenados, etc.).
2. **Tratamiento de datos** — Determinar qué pasos previos necesitan las imágenes (redimensionamiento, normalización, data augmentation, etc.).
3. **Integración** — Cómo se conectará este modelo con el resto de la infraestructura (almacenamiento y procesamiento).

### Evaluación y criterio clínico (el «porqué»)

La nota **no dependerá** de conseguir un porcentaje de acierto (accuracy) perfecto. En un entorno sanitario, es más importante entender cómo se comporta el modelo que su éxito estadístico.

**Es obligatorio:**

- **Analizar la matriz de confusión** — Identificar qué tipos de errores comete el modelo (por ejemplo, si confunde COVID-19 con neumonía).
- **Reflexión crítica** — Evaluar el impacto de estos errores desde un punto de vista médico. ¿Qué consecuencias tiene para el hospital un falso negativo en una enfermedad contagiosa?
- **Justificación técnica** — Explicar por qué se han tomado ciertas decisiones durante el entrenamiento y cuáles son las limitaciones reales del sistema desarrollado.

---

## Consideraciones éticas y legales

Dado que el sistema trabaja con datos del ámbito sanitario, se deberá incluir un **análisis crítico** sobre:

- Sesgos en los modelos de IA (por ejemplo, desigualdades en los datos)
- Riesgos en la toma de decisiones automatizadas
- Privacidad y protección de datos
- Limitaciones del sistema desarrollado

> Este apartado es **obligatorio** y forma parte esencial del proyecto.

---

## Enfoque del proyecto

El proyecto debe abordarse como un **desarrollo real** en un entorno profesional:

- Justificar decisiones técnicas
- Documentar el proceso
- Evaluar resultados
- Detectar limitaciones

No se trata únicamente de que el sistema funcione, sino de que **tenga sentido en un contexto real sanitario**.

---

## Entregables

### Proyecto (repositorio)

Se deberá entregar un repositorio con el sistema completo, que incluya:

- **Contenedores Docker** con toda la infraestructura:
  - Modelos de Inteligencia Artificial
  - Base de datos
  - Pipeline de datos
  - API (si aplica)
  - Dashboard o sistema de visualización
- Código organizado y estructurado correctamente
- Archivo `docker-compose` funcional
- Archivo **README** con instrucciones claras para ejecutar el sistema

El objetivo es que **cualquier persona** pueda levantar el proyecto completo con un único comando siguiendo el README.

### Presentación

| Aspecto | Detalle |
|---------|---------|
| Duración | 10–15 minutos |
| Contenido | Problema y solución propuesta |
| | Descripción de la arquitectura |
| | Demostración del funcionamiento (si es posible) |
| | Resultados obtenidos y conclusiones |

### Memoria técnica

Se deberá entregar un documento que incluya los siguientes apartados:

#### Descripción del problema

- Contexto del proyecto
- Objetivos planteados

#### Datos

- Fuentes utilizadas
- Proceso de limpieza y transformación

#### Arquitectura del sistema

- Diseño del pipeline de datos
- Infraestructura utilizada (Docker, servicios, etc.)
- Relación entre los distintos componentes

#### Modelos de Inteligencia Artificial

- Justificación del modelo seleccionado
- Proceso de entrenamiento
- Evaluación mediante métricas
- Resultados obtenidos

#### Automatizaciones

- Automatizaciones implementadas
- Integración dentro del sistema

#### Integraciones

- Flujo completo de datos
- Conexión entre los diferentes módulos

#### Diario de desarrollo con IA

- Herramientas utilizadas
- Ejemplos de prompts
- Problemas encontrados y soluciones

#### Justificaciones técnicas

- Decisiones tomadas durante el desarrollo
- Alternativas consideradas

#### Reflexión crítica

- Limitaciones del sistema
- Posibles mejoras
- Aplicación en un entorno real

#### Consideraciones éticas y legales

- Sesgos en los datos o modelos
- Privacidad
- Riesgos del sistema
