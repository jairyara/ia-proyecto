# Baseline supervisado — riesgo de retraso

Reporte generado por `python -m src.modelado.riesgo_retraso`.

## Datos

- Entrada: `pedidos.csv`
- Casos: 800
- Partición: 75% entrenamiento / 25% evaluación (estratificada, seed=20260828)
- Generador: distribuciones documentadas de `src/datos/sintetico.py` (triangular para distancia/volumen, uniforme para ventanas e índice de tráfico, elección ponderada para prioridad y binomial para indicadores).
- Tasa positiva en evaluación: 0.280

## Modelos comparados

| Modelo | Accuracy (test) | F1 (test) |
|---|---:|---:|
| `logistic_regression` | 0.8650 | 0.7327 |
| `random_forest` | 0.8350 | 0.6374 |

**Modelo elegido:** `logistic_regression` (mayor F1 en evaluación).

## Matriz de confusión del modelo elegido

| | Predicho 0 | Predicho 1 |
|---|---:|---:|
| **Real 0** | 136 | 8 |
| **Real 1** | 19 | 37 |

## Limitaciones

- Dataset sintético: las conclusiones aplican al generador, no al dominio.
- La partición fija controla comparabilidad; si se regenera el dataset cambian las métricas.
- El reporte documenta el criterio de selección (F1) sin garantizar el mejor modelo absoluto.

## Siguiente paso

- Evaluar en el seguimiento post-Corte 1 si se integra el dataset público *Amazon Last Mile Routing Challenge* (`data/amazon_pedidos.csv`) para contrastar el generador con datos reales.
