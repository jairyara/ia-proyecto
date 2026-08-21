# Pipeline supervisado de referencia

**Tema:** fundamentos de inteligencia artificial, entorno y primer modelo
reproducible.

## 1. Objetivo

Preparar la estructura acumulativa del proyecto y ejecutar el primer
clasificador supervisado indicado por la guía del curso.

## 2. Configuración

- Python objetivo: 3.13.x.
- Dataset: Iris, incluido en scikit-learn.
- Partición: 75% entrenamiento y 25% prueba, estratificada.
- Semilla: `RANDOM_STATE = 42`.
- Pipeline: `StandardScaler` + `LogisticRegression(max_iter=1000)`.

El experimento se ejecuta con:

```bash
python -m src.pipeline_iris
```

## 3. Resultados

- Muestras de entrenamiento: 112.
- Muestras de prueba: 38.
- Accuracy: 0.921.
- Matriz de confusión:

```text
[[12, 0, 0],
 [ 0, 12, 1],
 [ 0,  2, 11]]
```

## 4. Conclusiones y limitaciones

El pipeline reproduce el resultado esperado de la guía y demuestra un flujo
mínimo de datos, entrenamiento y evaluación. Iris es un dataset didáctico,
balanceado y de baja complejidad; por tanto, la métrica no representa el
rendimiento futuro del componente predictivo logístico. Su propósito es servir
como evidencia del entorno y como patrón reproducible para prácticas
posteriores.

