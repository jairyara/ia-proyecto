# ADR-011 — Riesgo heurístico Amazon: modelo académico frente a regla explícita

- **Estado:** Aceptado para el laboratorio y la simulación; **no** aprueba predicción de retrasos observados ni decisiones autónomas.
- **Fecha:** 2026-10-14.
- **Alcance:** Semana 11 de Órbita y la futura señal de riesgo de la Torre de Control.
- **Responsables:** equipo del Proyecto 8; revisión operativa pendiente para el Corte 3.

## Contexto y problema

El proyecto ya dispone de 14.411 paradas Amazon Last Mile curadas y una etiqueta `retrasado_estimado`. La guía académica pide comparar familias de modelos y sustentar una decisión. El benchmark adapta cuatro familias al **dataset propio Amazon**, no copia `load_digits` ni mezcla las 800 filas sintéticas de Semana 2 o las 200 imágenes visuales. Se excluyen 100 estaciones sin entrega, se reservan rutas completas y se evalúan 14.311 paradas `Dropoff`.

La etiqueta Amazon **no mide tardanza real**. `src/datos/amazon.py` la construye con tres reglas. En este CSV las cláusulas «servicio planificado >150 s y volumen >0,03 m³» o «distancia >15 km y al menos 3 paquetes» reproducen todos los positivos; la condición que contiene `secuencia_real` no aporta positivos exclusivos. Un modelo con métricas casi perfectas puede estar **imitando exactamente esa heurística**. El [informe](semana11.md) da el protocolo, CSV, matrices y limitaciones.

## Criterios y opciones

| Opción | Evidencia test (3.509 paradas, 251 positivos) | Ventaja | Límite |
|---|---|---|---|
| Logistic | F1 0,4449; 55 FN / 434 FP | Simple y auditable | Frontera lineal inadecuada para estas conjunciones de umbrales |
| **Random Forest** | **F1 0,9980; 0 FN / 1 FP** | Mejor imitador de la etiqueta en el protocolo | No aporta valor probado por encima de la regla que creó la etiqueta |
| MLP | F1 0,9494; 7 FN / 19 FP | Familia no lineal comparativa | Más ajuste y menor trazabilidad; advertencias en metadatos si aparecen |
| HistGradientBoosting | F1 0,9920; 2 FN / 2 FP | Retador tabular muy cercano a Forest | Tampoco demuestra retraso observado; no gana este test |
| Regla explícita existente | Reproduce los 1.023 positivos del CSV elegible | Determinista, transparente, cero costo de entrenamiento | Solo refleja una definición heurística; necesita validación operativa |

Todos los modelos recibieron las mismas siete variables disponibles antes del despacho, pipelines sin fuga de transformaciones, test de rutas disjuntas (~75/25) y umbral F2 elegido exclusivamente en train mediante cinco pliegues agrupados. `route_id` no es variable predictora. `secuencia_real`, ID, fecha y otras columnas potencialmente posteriores o identificadoras se excluyeron. La prevalencia positiva es 7,15 %: accuracy por sí sola sería engañosa. Los tiempos del CSV son solo del ajuste/inferencia local, no del flujo de Torre.

## Decisión

1. **Resultado académico:** declarar **Random Forest ganador del benchmark de aprendizaje de la heurística Amazon**, con HistGradientBoosting como retador cercano. No seleccionar Hist por una expectativa del paper ni mantener la elección Logistic procedente del benchmark sintético anterior.
2. **Diseño del MVP simulado:** conservar la **regla explícita** como fuente auditable del riesgo heurístico; no reemplazarla por Forest solo porque la copia con F1 0,9980. El modelo puede quedar como comparador o «challenger» en Órbita, pero no autoriza despacho, bloqueo ni cuarentena. Si se integra un score, debe exhibirse como *estimación heurística* con versión, origen y revisión humana.
3. **Decisión aplazada para riesgo real:** ningún modelo de esta tabla se aprueba para predecir demoras reales. Una nueva etiqueta con hora prometida y hora efectiva, un corte temporal y costos FN/FP acordados requieren **nuevo benchmark y revisión/sucesor de ADR** antes del uso con clientes.

## Consecuencias y disparadores de revisión

**Positivo:** el laboratorio usa datos logísticos del proyecto, compara cuatro familias bajo rutas reservadas y evidencia que la complejidad del modelo no equivale a valor operativo. **Costo:** no entrega todavía un predictor validado de demoras observadas; la Torre debe distinguir señal heurística de decisión humana. **Riesgo si se ignora el límite:** una F1 casi perfecta podría venderse equivocadamente como capacidad de anticipación cuando el objetivo es una regla escrita en código.

Revisar este ADR cuando existan etiquetas observadas, cambie la definición de retraso, se establezca el momento de predicción y se midan generalización temporal, calibración, carga, falsos negativos y carga de falsas alertas. Las [dudas concretas del Corte 3](../docs/decision-tecnologica-y-plan-torre-control.md#6-pendientes-que-requieren-validación-del-equipo) reúnen esas tareas. La decisión de Python/FastAPI, interoperabilidad HTTP, servidor y OCR tiene justificación separada en el mismo plan; este benchmark no prueba rendimiento de infraestructura.

## Trazabilidad y fuentes

- [`artifacts/benchmark.csv`](../artifacts/benchmark.csv) y [`artifacts/semana11_benchmark.json`](../artifacts/semana11_benchmark.json): cuatro filas, matriz por modelo, split y hashes.
- [`src/semana11_benchmark.py`](../src/semana11_benchmark.py) y [`src/datos/amazon.py`](../src/datos/amazon.py): evaluación y construcción de la etiqueta.
- [AWS Prescriptive Guidance, proceso de ADR](https://docs.aws.amazon.com/prescriptive-guidance/latest/architectural-decision-records/adr-process.html).
- [scikit-learn, separación por grupos](https://scikit-learn.org/stable/modules/cross_validation.html#cross-validation-iterators-for-grouped-data) y [fuga de datos](https://scikit-learn.org/stable/common_pitfalls.html#data-leakage).
