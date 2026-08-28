# Plan de fases — Sistema inteligente para logística

**Proyecto 8 · Inteligencia Artificial · 10.º semestre · 18 semanas**  
**Equipo:** Jair Yara y Catherinne Gutierrez  
**Cortes oficiales:** semana 6 (`v1.0.0`), semana 12 (`v2.0.0`) y semana
18 (`v3.0.0`).

**Fuente primaria:**
[`docs/justificacion-proyecto-08.pdf`](docs/justificacion-proyecto-08.pdf),
contrastada con los materiales confirmados del curso.

## Visión del sistema

El sistema planifica rutas de reparto sobre un grafo de la zona de entrega
mediante A*, anticipa condiciones de la operación con aprendizaje automático,
valida los planes con reglas logísticas explícitas y replantea la solución ante
eventos como pedidos nuevos o vías cerradas. Toda decisión debe conservar
evidencia suficiente para explicar qué datos, heurística, predicción o regla la
produjo.

## Principios de implementación

- Cada práctica confirmada del curso se aplica al proyecto en cuanto se
  publica.
- El repositorio es acumulativo y autocontenido; `../ia-semestre` funciona como
  referencia académica, no como dependencia de ejecución.
- Cada componente declara entradas, salidas, supuestos y una forma objetiva de
  validación.
- Los algoritmos se comparan bajo el mismo escenario y configuración.
- Datos sintéticos, reglas y resultados deben ser reproducibles.
- Las decisiones no confirmadas se mantienen abiertas hasta contar con la guía
  del curso o un acuerdo explícito del equipo.

## Estado actual

- [x] Estructura `src/`, `data/`, `notebooks/`, `artifacts/`, `reports/` y
  `tests/`.
- [x] Configuración reproducible, convenciones de commits y changelog.
- [x] README con problema, justificación, objetivos y arquitectura prevista.
- [x] Taxonomía del dominio: áreas de IA vinculadas a los componentes.
- [x] Clasificador simbólico como línea base de requerimientos logísticos.
- [x] 20 casos logísticos, vocabulario propio del dominio, pruebas
  automatizadas e informes reproducibles.
- [x] Baseline supervisado de riesgo de retraso: generador sintético
  reproducible (`src/generador_pedidos.py`, 800 casos etiquetados,
  seed 20260828) y pipeline con LogisticRegression y RandomForest
  comparados por F1 y validados con accuracy y matriz de confusión
  (`src/modelo_riesgo.py`, `reports/riesgo-retraso.md`).
- [ ] Repositorio privado en GitHub e invitación de escritura enviada a
  `CatherinneG`.
- [x] Dataset público **Amazon Last Mile Routing Challenge** preparado y
  curado (`src/extraer_datos_amazon.py`, `data/amazon_pedidos.csv`,
  `data/amazon_rutas_muestra.json`, `reports/datos-amazon-last-mile.md`) para
  transición / contraste con datos reales cuando se requiera.
- [ ] Grafo de entregas, A* y línea base no informada pendientes para el
  corte 1.

## Arquitectura incremental

```text
pedidos + red vial + eventos
            │
            ▼
  predicción de la operación
            │
            ▼
  búsqueda y planificación de rutas
            │
            ▼
  validación de reglas operativas
            │
            ▼
       plan explicable
            │
   evento ──┴──► replanificación
```

Los módulos intercambiarán estructuras de datos explícitas. La capa de reglas
no debe quedar acoplada al algoritmo de búsqueda, y las predicciones deben
conservar su versión y métricas para poder auditar el plan resultante.

## Roadmap

Las semanas 4 en adelante son provisionales hasta que el profesor publique el
material correspondiente.

| Semana | Contenido | Aplicación |
|---:|---|---|
| 2 | Fundamentos y entorno | Repositorio y ejecución reproducible |
| 3 | Taxonomía de IA | Mapeo del dominio y línea base simbólica |
| 4–6 | Búsqueda y aprendizaje supervisado | Grafo, A*, línea base no informada, dataset y modelo predictivo |
| **6** | **Corte 1** | **Planifica rutas — `v1.0.0`** |
| 7–12 | Reglas y representación del conocimiento | Motor de restricciones, ontología y base de conocimiento |
| **12** | **Corte 2** | **Opera con restricciones — `v2.0.0`** |
| 13–18 | Visión, agentes e integración | Verificación de paquetes, eventos y replanificación |
| **18** | **Corte 3** | **Sistema integrado — `v3.0.0`** |

## Alcance por corte

### Corte 1 — planifica rutas (`v1.0.0`)

- grafo de entregas con representación numérica y simbólica;
- matrices de distancias y tiempos;
- A* con heurística de distancia;
- búsqueda no informada como línea base, comparada por costo y nodos
  expandidos;
- pedidos sintéticos y modelo predictivo validado con accuracy, F1 y matriz de
  confusión;
- jornada pequeña ejecutada de extremo a extremo.

### Corte 2 — opera con restricciones (`v2.0.0`)

- reglas trazables de capacidad, ventanas horarias, prioridad y cadena de frío;
- ontología del dominio y base de conocimiento persistente;
- integración entre predicción, búsqueda y validación;
- comparación del modelo predictivo contra las métricas del primer corte.

### Corte 3 — sistema integrado (`v3.0.0`)

- verificación visual de paquetes;
- ciclo planificar → ejecutar → percibir → replanificar, con condición de
  parada;
- tres casos demostrativos del sistema completo;
- pruebas, métricas finales y reporte técnico de decisiones, limitaciones y
  riesgos.

## Decisiones abiertas

Estas decisiones afectan la comparabilidad de los experimentos y deben
resolverse antes de implementar los módulos relacionados:

| Decisión | Opciones iniciales | Criterio de cierre |
|---|---|---|
| Zona de entrega | Grafo sintético o zona real simplificada | Fuente reproducible, tamaño manejable y coordenadas disponibles |
| Pedidos por jornada | Tamaño y distribución por definir | Suficientes casos para entrenamiento, validación y escenarios extremos |
| Tarea predictiva (cerrada) | Riesgo de retraso | Métrica interpretable (accuracy, F1) e integración con rutas |
| Variables de pedidos (cerrada) | Distancia, volumen, prioridad, ventana, frío, hora pico, zona, tráfico | Relación justificada con la etiqueta y sin fuga de datos |
| Fuente del dataset | Generador sintético con distribuciones citadas (seguimiento: Amazon Last Mile post-Corte 1) | Reproducibilidad y documentación de distribuciones |
| Verificación visual | Conteo, estado o lectura de etiqueta | Correspondencia con el material del curso y datos obtenibles |
| Reporte de avance | Frecuencia y formato por corte | Evidencia clara sin duplicar los reportes por tema |

## Riesgos y mitigaciones

- **Sesgo de los datos sintéticos:** documentar las distribuciones y probar
  escenarios fuera del caso promedio.
- **Heurística no admisible:** verificar la relación entre distancia directa y
  costo real antes de interpretar los resultados de A*.
- **Fuga de datos:** ajustar transformaciones únicamente con entrenamiento y
  mantener una partición de evaluación independiente.
- **Reglas contradictorias:** definir prioridad, registrar cada activación y
  probar conflictos deliberadamente.
- **Crecimiento del alcance:** cada corte debe conservar una demostración
  vertical funcional antes de agregar nuevos módulos.
