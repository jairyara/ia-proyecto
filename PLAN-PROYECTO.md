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
  (`src/modelo_riesgo.py`, `reports/sem-02-riesgo-retraso.md`).
- [ ] Repositorio privado en GitHub e invitación de escritura enviada a
  `CatherinneG`.
- [x] Dataset público **Amazon Last Mile Routing Challenge** preparado y
  curado (`src/extraer_datos_amazon.py`, `data/amazon_pedidos.csv`,
  `data/amazon_rutas_muestra.json`, `reports/sem-02-datos-amazon-last-mile.md`) para
  transición / contraste con datos reales cuando se requiera.
- [x] Grafo de entregas, A* con heurística Haversine admisible, línea base no
  informada (Dijkstra/BFS) y replanificación dinámica implementados y validados
  (`src/busqueda/`, `reports/sem-04-busqueda-rutas.md`).

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

Material confirmado del curso hasta la **Semana 4** (fuentes: `Guia_Explicativa_Semana_04_IA_Estudiantes.pdf`, `Semana_04_Marco_tecnologico_de_la_inteligencia_artificial_Clase.pptx` y `../ia-semestre/TEMATICAS.md`). Las semanas 5 en adelante se actualizan según se publique el material.

| Semana | Contenido oficial | Aplicación al proyecto logístico | Estado |
|---:|---|---|---|
| **2** | Fundamentos y entorno | Repositorio reproducible y baseline predictivo (`src.modelado.riesgo_retraso`) | **Completado** |
| **3** | Taxonomía de IA | Mapeo de 7 áreas y clasificador simbólico (`src.clasificacion.requerimientos`) | **Completado** |
| **4** | Marco tecnológico y búsqueda | Grafo vial, A* con heurística admisible Haversine, línea base no informada y replanificación (`src.busqueda`) | **Completado** |
| 5–6 | Integración Corte 1 | Validación cruzada, jornada extremo a extremo y entrega `v1.0.0` | Pendiente |
| **6** | **Corte 1** | **Planifica rutas — `v1.0.0`** | **Meta hito** |
| 7–12 | Reglas y representación del conocimiento | Motor de restricciones, ontología y base de conocimiento (`src.reglas`) | Pendiente |
| **12** | **Corte 2** | **Opera con restricciones — `v2.0.0`** | **Meta hito** |
| 13–18 | Visión, agentes e integración | Verificación de paquetes, eventos y replanificación (`src.vision`, `src.agentes`) | Pendiente |
| **18** | **Corte 3** | **Sistema integrado — `v3.0.0`** | **Meta hito** |

## Especificación técnica — Semana 4: Búsqueda y Planificación de Rutas

Basada en los lineamientos oficiales de la guía de Semana 4 (*Espacios de estados, A\*, Heurísticas y Decisiones*):

### 1. Formulación formal del espacio de estados

| Componente | Definición formal | Implementación en logística |
|---|---|---|
| **Estado ($s$)** | $s = (\text{nodo\_actual}, t_{\text{acum}}, \text{paradas\_visitadas})$ | Posición geográfica actual del repartidor en el grafo y estado de entrega. |
| **Acciones ($A(s)$)** | $a \in \text{vecinos}(s.\text{nodo})$ accesibles por la red vial | Desplazarse a una parada/intersección vecina no bloqueada. |
| **Transición ($T(s, a)$)** | $s' = (a, s.t_{\text{acum}} + \text{costo}(s, a), s.\text{visitadas} \cup \{a\})$ | Actualización de la posición del vehículo y acumulación del costo de viaje. |
| **Meta ($Goal$)** | $\text{nodo\_actual} = \text{nodo\_destino}$ | Parada objetivo alcanzada (o depósito final completando el circuito). |
| **Costo real ($g(n)$)** | $g(n) = \sum \text{tiempo\_viaje}(u, v)$ en segundos (o distancia en km) | Tiempo real medido en la matriz de adyacencia de la red vial. |
| **Heurística ($h(n)$)** | $h(n) = \frac{\text{haversine\_km}(n, \text{meta})}{v_{\max}}$ | Estimación en línea recta en segundos hacia la meta dividida por la velocidad máxima de la flota ($v_{\max} \approx 80\text{ km/h}$). |

> [!NOTE]
> **Garantía de admisibilidad:** Como la distancia geodésica en línea recta es la distancia mínima absoluta entre dos puntos ($\text{Haversine} \le \text{distancia\_vial}$), y dividida por la velocidad máxima estimada nunca sobreestima el tiempo real de viaje ($h(n) \le h^*(n)$), la heurística es **admisible** y **consistente**, garantizando que $A^*$ encontrará el camino óptimo.

### 2. Módulos de software a implementar (`src/busqueda/`)

- **`src/busqueda/grafo.py`:** Clase `GrafoEntregas` que modela nodos (paradas/estaciones con `lat`, `lng`), aristas ponderadas con matrices de tiempo (usando las topologías de `data/amazon_rutas_muestra.json`), y método para simular bloqueos de vías.
- **`src/busqueda/a_estrella.py`:** Algoritmo $A^*$ con cola de prioridad (`heapq`), función de costo $f(n) = g(n) + h(n)$, registro de nodos expandidos y reconstrucción de ruta explicable con auditoría paso a paso.
- **`src/busqueda/no_informada.py`:** Búsqueda no informada de referencia (Costo Uniforme / Dijkstra / BFS) para comparar de forma objetiva la reducción en el espacio de exploración.
- **`src/busqueda/replanificacion.py`:** Simulación del ciclo dinámico de replanificación ante eventos imprevistos (vía cerrada o congestión repentina), recalculando la ruta óptima desde el estado actual.

### 3. Métricas y comparación a registrar

Para cada escenario de prueba se registrarán y contrastarán en tabla Markdown:
1. **Costo total de la solución ($g(\text{meta})$):** Verificación de optimalidad (ambos algoritmos deben encontrar el mismo costo mínimo).
2. **Nodos expandidos / explorados:** Evidencia cuantitativa de la reducción del espacio de búsqueda por la heurística.
3. **Tiempo de ejecución ($\mu s$ / $ms$):** Medición del trade-off de cómputo frente a la búsqueda no informada.
4. **Comportamiento ante bloqueo (Replanificación):** Verificación de que el sistema encuentra la ruta alternativa óptima cuando se bloquea una vía del trayecto.

### 4. Criterios de validación del curso (Las 3 condiciones)

1. **REALIZADO:** Módulo `src/busqueda/`, pruebas `tests/test_busqueda.py` y reporte `reports/sem-04-busqueda-rutas.md`.
2. **FUNCIONA:** Ejecución reproducible en Python 3.13.x sin dependencias externas fuera de `requirements.txt`.
3. **COINCIDE:** Identificación formal de los 5 elementos (Estado, Acción, Transición, Meta, Costo) y comprobación de optimalidad y admisibilidad.

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
| Zona de entrega (cerrada) | Topologías reales de Amazon Last Mile (`data/amazon_rutas_muestra.json`) y cuadrícula sintética | Coordenadas reales (`lat`, `lng`), matrices de tiempo $N \times N$ y soporte de simulación de vías bloqueadas |
| Pedidos por jornada | Tamaño y distribución por definir | Suficientes casos para entrenamiento, validación y escenarios extremos |
| Tarea predictiva (cerrada) | Riesgo de retraso | Métrica interpretable (accuracy, F1) e integración con rutas |
| Variables de pedidos (cerrada) | Distancia, volumen, prioridad, ventana, frío, hora pico, zona, tráfico | Relación justificada con la etiqueta y sin fuga de datos |
| Fuente del dataset (cerrada) | Generador sintético (`data/pedidos.csv`) y dataset curado Amazon Last Mile (`data/amazon_pedidos.csv`) | Reproducibilidad, distribuciones documentadas y datos reales para búsqueda $A^*$ |
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
