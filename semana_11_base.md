# Base de Trabajo · Semana 11: Benchmark de Modelos y Registro de Decisiones de Arquitectura (ADR)

> **Nota de vigencia (2026-10-14):** este borrador conserva propuestas iniciales, **no el protocolo ni la decisión finales**. La implementación y cifras verificadas están en [`reports/semana11.md`](reports/semana11.md), [`artifacts/benchmark.csv`](artifacts/benchmark.csv) y [`reports/semana11_adr.md`](reports/semana11_adr.md); el plan de Torre está en [`docs/decision-tecnologica-y-plan-torre-control.md`](docs/decision-tecnologica-y-plan-torre-control.md). Se compararon cuatro modelos sobre **14.311 entregas Amazon**, con `retrasado_estimado` heurístico: Forest ganó el benchmark, pero la regla explícita sigue siendo la señal para simulación. Los **800 pedidos sintéticos** permanecen en Semana 2, no son un segundo benchmark de Semana 11. `load_digits`, `random_state=42`, cifras de servidor/costo y elección anticipada de SVC más abajo son referencias o hipótesis del borrador, **no hechos de la implementación**.

> **Documento temporal de preparación en la raíz del repositorio**  
> Sirve como guía de implementación para `src/semana11_benchmark.py`, `artifacts/benchmark.csv` y `reports/semana11_adr.md`.

---

## 1. Alcance Académico y Requerimientos de la Semana 11

La práctica de la Semana 11 se centra en **aprender a tomar decisiones técnicas con evidencia empírica**, evaluando tres modelos de diferentes familias sobre un mismo protocolo reproducible.

### Entregables exigidos por la rúbrica:
1. **Script de Benchmark:** `src/semana11_benchmark.py`
2. **Evidencia cuantitativa generada:** `artifacts/benchmark.csv`
3. **Registro de Decisión de Arquitectura:** `reports/semana11_adr.md`
4. **Commit sugerido:** `semana11-benchmark`

### Protocolo experimental canónico (Cuarteto de evaluación):
* **Dataset de práctica:** `sklearn.datasets.load_digits` (1.797 imágenes de 8×8 píxeles aplanadas a 64 características).
* **Partición:** 75% entrenamiento / 25% prueba (`test_size=0.25`, `random_state=42`, `stratify=y`).
* **Métricas medidas:** `accuracy` en el conjunto de prueba y tiempo de ajuste `fit_seconds` con `time.perf_counter`.
* **Modelos evaluados en el benchmark:**
  ```python
  from sklearn.linear_model import LogisticRegression
  from sklearn.ensemble import RandomForestClassifier, HistGradientBoostingClassifier
  from sklearn.neural_network import MLPClassifier
  from sklearn.pipeline import make_pipeline
  from sklearn.preprocessing import StandardScaler

  models = {
      # Los 3 modelos obligatorios de la rúbrica de clase:
      "logistic": make_pipeline(StandardScaler(), LogisticRegression(max_iter=1500)),
      "forest": RandomForestClassifier(n_estimators=250, random_state=42, n_jobs=-1),
      "mlp": make_pipeline(StandardScaler(), MLPClassifier(hidden_layer_sizes=(64,), max_iter=350, random_state=42)),
      # El 4.° modelo retador del estado del arte para contrastar empíricamente:
      "hist": HistGradientBoostingClassifier(random_state=42),
  }
  ```

---

## 2. Marco Metodológico para el ADR (Basado en Estándares AWS y Google Cloud)

Siguiendo las mejores prácticas de la industria, el informe `reports/semana11_adr.md` adoptará la estructura de **AWS Prescriptive Guidance**, complementada con la concisión del formato **MADR (Markdown Any Architecture Decision Records)** y **Google Cloud Architecture Framework**:

* **Fuentes de referencia recomendadas:**
  * [AWS Prescriptive Guidance — Proceso de ADR](https://docs.aws.amazon.com/es_es/prescriptive-guidance/latest/architectural-decision-records/adr-process.html)
  * [AWS Prescriptive Guidance — Documento PDF](https://docs.aws.amazon.com/es_es/prescriptive-guidance/latest/architectural-decision-records/architectural-decision-records.pdf#adr-process)
  * [AWS Architecture Blog — Master Architecture Decision Records](https://aws.amazon.com/blogs/architecture/master-architecture-decision-records-adrs-best-practices-for-effective-decision-making/)
  * [Google Cloud Architecture Framework — Decision Records](https://docs.cloud.google.com/architecture/architecture-decision-records)
  * [GitHub Community Standard — ADR / MADR](https://github.com/architecture-decision-record/architecture-decision-record)

### Estructura estándar sugerida para `reports/semana11_adr.md`:

```markdown
# ADR-011: Selección de Componentes Predictivos y Clasificadores

- **Estado:** Aceptado (Accepted)
- **Fecha:** 2026-10-XX
- **Autores:** Equipo de Desarrollo · Proyecto 8
- **Contexto del Problema:** Necesidad de predecir riesgo operativo y clasificar estados de carga bajo restricciones de baja latencia y costos mínimos de infraestructura en centros de distribución.

## Contexto y Declaración del Problema
Descripción del reto logístico: balancear precisión predictiva, tiempo de cómputo, interpretabilidad para el sistema híbrido y factibilidad de despliegue en clientes corporativos sin tarjetas GPU dedicadas.

## Opciones Evaluadas
1. **Opción 1: Regresión Logística (`logistic` - Línea base lineal)**
   - Pros: Inferencia en < 2 ms, coeficientes interpretables para el operador, bajo consumo de memoria.
   - Contras: Capacidad limitada ante relaciones altamente no lineales.
2. **Opción 2: Random Forest (`forest` - Ensamble Bagging)**
   - Pros: Modela interacciones no lineales sin requerir escalado numérico, robusto a sobreajuste.
   - Contras: Mayor tiempo de entrenamiento (`fit_seconds`), mayor huella en memoria (250 árboles).
3. **Opción 3: MLPClassifier (`mlp` - Red Neuronal Feedforward)**
   - Pros: Capacidad de representación de funciones complejas.
   - Contras: Tiempo de ajuste significativamente más alto, sensibilidad crítica a hiperparámetros y normalización, opacidad de caja negra.
4. **Opción 4: HistGradientBoostingClassifier (`hist` - Ensamble Boosting por Histogramas)**
   - Pros: Corrección secuencial de errores residuales, entrenamiento y predicción ultrarrápidos gracias a discretización en 256 bins, no requiere escalado manual previo, excelente generalización en datos estructurados.
   - Contras: Requiere mayor atención al `learning_rate` y parada temprana; menor explicabilidad visual directa que un árbol individual.

## Evidencia Experimental
(Inserción de la tabla generada en `artifacts/benchmark.csv` con las 4 filas evaluadas bajo el mismo split: `modelo`, `accuracy`, `fit_seconds`).

## Decisión de Arquitectura
- **Para la entrega académica:** Se cumple al 100% con los tres modelos canónicos de la guía y se añade `hist` como modelo retador para contrastar la teoría con números reales.
- **Para el Sistema Productivo Logístico:** 
  - Se conserva `LogisticRegression` para el módulo auditable de riesgo.
  - Se proyecta `HistGradientBoosting` en lugar de `RandomForest` / `MLP` para máxima precisión tabular.
  - Para inspección visual de paquetes, se adopta `SVC` sobre el vector de 53 descriptores de textura de la Semana 10, descartando el `MLP` crudo.

## Consecuencias y Trade-offs
- **Positivas:** Reducción drástica del costo operativo (ejecución 100% en CPU estándar), compatibilidad con microservicios en contenedores ligeros (<1 GB RAM), respuesta en tiempo real.
- **Negativas / Mitigaciones:** Se renuncia al uso de redes neuronales profundas en esta etapa, mitigado por el hecho de que en datos tabulares los árboles superan empíricamente al deep learning.

### Impacto en Infraestructura y Recursos (Specs para Producción)
* **Cómputo:** La solución opera 100% sobre CPU estándar (2 vCPU, 2 GB RAM); no requiere tarjetas GPU dedicadas ni clústeres distribuidos.
* **Latencia de inferencia:** Inferencia ultrarrápida (< 15 ms por paquete) adecuada para líneas de escaneo en tiempo real.
* **Costo operativo cloud:** Se puede desplegar en instancias mínimas (ej. AWS `t4g.small` o contenedor Docker básico) por ~$15 a $25 USD/mes, frente a los >$350 USD/mes que exigiría mantener instancias GPU para inferencia de redes neuronales profundas.
* **Mantenibilidad:** Despliegue en un único contenedor sin dependencias complejas de CUDA o drivers propietarios.
```

---

## 3. Sustentación Científica: ¿Por qué descartar el MLP en Datos Tabulares?

Para defender técnicamente por qué el Perceptrón (MLP) no es la opción ganadora en la arquitectura final, se incorpora como evidencia formal el estudio de referencia de NeurIPS 2022:

* **Referencia bibliográfica:**  
  Grinsztajn, L., Oyallon, E., & Varoquaux, G. (2022). *Why do tree-based models still outperform deep learning on typical tabular data?* Advances in Neural Information Processing Systems (NeurIPS 2022).  
  **Enlace al paper en arXiv:** [https://arxiv.org/pdf/2207.08815](https://arxiv.org/pdf/2207.08815)

### Argumentos del paper aplicables a nuestro proyecto:
1. **Fronteras de decisión escalonadas / ortogonales:** Los datos tabulares logísticos (ej. `distancia > 15 km` y `hora_pico == 1`) presentan discontinuidades naturales que los árboles de decisión segmentan con facilidad. Las redes neuronales asumen superficies suaves y sobreajustan intentando aproximar escalones.
2. **Invariancia a transformaciones monótonas:** Los modelos de árboles son inmunes a escalas relativas entre variables numéricas, mientras que los gradientes de un MLP se descalibran ante rangos dispares o outliers.
3. **Eficiencia computacional:** Modelos basados en histogramas (`HistGradientBoosting` / `LightGBM`) alcanzan convergencia órdenes de magnitud más rápido que una red neuronal, requiriendo una fracción de memoria y CPU.

---

## 4. Notas Clave para la Implementación en el Repositorio

* [x] No modificar las dependencias congeladas del proyecto para la Semana 11; `scikit-learn`, `pandas` y `numpy` ya están disponibles en `.venv`.
* [x] Mantener `artifacts/benchmark.csv` determinista y reproducible con `random_state=42`.
* [x] La redacción del ADR debe vincular la decisión con los requerimientos logísticos analizados en la Semana 03 (REQ-008 y REQ-015) y la proyección a la Torre de Control del Corte 3.
