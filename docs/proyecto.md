# Proyecto y propuesta del dashboard

**Proyecto 8 · Inteligencia Artificial · 10.º semestre · 18 semanas**
**Equipo:** Jair Yara y Catherinne Gutierrez
**Cortes oficiales:** semana 6 (`v1.0.0`), semana 12 (`v2.0.0`) y semana
18 (`v3.0.0`).

**Fuente primaria:**
[`docs/justificacion-proyecto-08.pdf`](justificacion-proyecto-08.pdf),
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
- Las entregas de Semanas 2–7 conservan sus datos, contratos y comportamiento.
  Desde el acuerdo del 2026-09-22, las funcionalidades nuevas usan base de datos,
  migraciones y API; no se migra retroactivamente el código académico anterior.

## Estado actual

- [x] PostgreSQL, SQLAlchemy y Alembic con Python 3.14 y compatibilidad histórica.
- [x] Importación idempotente de 14.411 paradas, 100 rutas y 17 estaciones.
- [x] 200 imágenes sintéticas auditadas y 200 asociaciones simuladas persistidas.
- [ ] API e interfaz de inspección; diseño ajustable cuando llegue la guía.

Comandos y arquitectura vigente: [guía técnica](guia-tecnica.md).

- [x] Estructura `src/`, `data/`, `artifacts/`, `reports/` y
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
- [x] Dashboard didáctico **Órbita** para sustentar los componentes de Semanas
  2–4: API FastAPI desacoplada (`api/`), SPA React (`dashboard/`), trazas de
  búsqueda, simulación predictiva, reglas explicables y ejecución reproducible
  con Docker. El core académico en `src/` conserva sus contratos.
- [x] Workspace didáctico común por semana con navegación ascendente, pestañas
  **Laboratorio / Código explicado / Informe**, lectura segura del código real
  con explicación línea a línea y visualización de reportes Markdown. El
  frontend se gestiona exclusivamente con `pnpm@11.25.0` y lockfile congelado.
- [x] Sistema híbrido trazable de la Semana 5 integrado al dashboard:
  5 reglas expertas del dominio logístico con palabra detonante visible,
  recuperación documental TF-IDF + coseno sobre 10 protocolos SOP
  (`data/base_conocimiento.txt`) y clasificación supervisada con distribución
  de probabilidad (`src/hibrido/`, `api/hibrido`,
  `reports/sem-05-sistema-hibrido.md`).
- [x] Representaciones del reconocimiento de Semana 7: vectores de 14.411
  paradas Amazon con euclidiana cruda y normalizada por IQR,
  traducción a hechos mediante P75, reglas auditables y AFD de protocolo POD
  (`src/representaciones/`, `api/representaciones`,
  `reports/sem-07-representaciones.md`).

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

La capa de presentación sigue la misma separación: `api/services/` transforma
los resultados del core en DTO y trazas didácticas; `api/services/contenido.py`
solo expone archivos e informes registrados en un catálogo seguro; y
`dashboard/` consume esos contratos. Si el artefacto supervisado no existe en
un clon limpio, la API lo reconstruye con la semilla y partición documentadas
antes de inferir.

## Próximo trabajo

Recibir la guía, contrastar sus requisitos con lo existente y ajustar el
[dashboard actual](#dashboard-actual-y-propuesta-mlp) y la documentación al
terminar la actividad. La persistencia, la API de inspección y la interfaz del
piloto están disponibles; OpenAPI documenta los contratos actuales en `/docs`.
CI consolidada y el MLP visual siguen pendientes. No fijar tarea,
preprocesamiento, arquitectura ni métricas del MLP sin la guía.

Trabajar por incrementos revisables con pruebas y confirmación del usuario;
no migrar retroactivamente las entregas académicas anteriores.

## Roadmap

Material confirmado del curso hasta la **Semana 7** (fuentes: `Guia_Explicativa_Semana_04_IA_Estudiantes.pdf`, `Semana_04_Marco_tecnologico_de_la_inteligencia_artificial_Clase.pptx`, `Semana_05_IA_Marco_Tecnologico_Clase_final.pptx`, `Semana_07_Representaciones_del_reconocimiento_Clase.pptx`, `Explicacion_Semana_07.md` y `../ia-semestre/TEMATICAS.md`). Las semanas posteriores se actualizan según se publique el material.

| Semana | Contenido oficial | Aplicación al proyecto logístico | Estado |
|---:|---|---|---|
| **2** | Fundamentos y entorno | Repositorio reproducible y baseline predictivo (`src.modelado.riesgo_retraso`) | **Completado** |
| **3** | Taxonomía de IA | Mapeo de 7 áreas y clasificador simbólico (`src.clasificacion.requerimientos`) | **Completado** |
| **4** | Marco tecnológico y búsqueda | Grafo vial, A* con heurística admisible Haversine, línea base no informada y replanificación (`src.busqueda`) | **Completado** |
| **5** | Marco tecnológico: sistemas híbridos | Reglas expertas + TF-IDF/coseno + regresión logística con trazabilidad, demostrable en el dashboard (`src.hibrido`) | **Completado** |
| 6 | Integración Corte 1 | Validación cruzada, jornada extremo a extremo y entrega `v1.0.0` | **Completado** |
| **6** | **Corte 1** | **Planifica rutas — `v1.0.0`** | **Meta hito** |
| **7** | Representaciones del reconocimiento | Vectores Amazon, euclidiana/IQR, hechos P75 y AFD POD (`src.representaciones`) | **Completado** |
| Pre-8 | Hito técnico acordado por el equipo, no actividad oficial adicional | BD, migraciones, seed Amazon, piloto visual sintético y dashboard de inspección | Persistencia y API/interfaz de lectura completadas; MLP pendiente de guía |
| 8 | MLP con imágenes, indicado por el equipo; guía pendiente | Ejercicio visual apoyado en el piloto de 200 imágenes; diseño y evaluación por confirmar | Pendiente de guía |
| 9–12 | Reglas y representación del conocimiento, sujeto a materiales oficiales | Motor de restricciones, ontología y base de conocimiento (`src.reglas`) | Pendiente |
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
2. **FUNCIONA:** Ejecución reproducible en el entorno elegido Python 3.14.x sin dependencias externas fuera de `requirements.txt`.
3. **COINCIDE:** Identificación formal de los 5 elementos (Estado, Acción, Transición, Meta, Costo) y comprobación de optimalidad y admisibilidad.

## Especificación técnica — Semana 7: Representaciones del reconocimiento

Basada en `Semana_07_Representaciones_del_reconocimiento_Clase.pptx` y
`Explicacion_Semana_07.md`:

1. **Datos del proyecto:** procesa las 14.411 paradas de 100 rutas en
   `data/amazon_pedidos.csv`; usa distancia al depósito, volumen total y tiempo
   de servicio, todas sin nulos.
2. **Método numérico:** compara cada vector contra la mediana del dataset. Se
   conserva la euclidiana cruda como evidencia didáctica y se usa como medida
   principal la euclidiana después de dividir por el IQR de cada variable.
3. **Método simbólico:** valores que superan el P75 originan
   `parada_lejana`, `volumen_alto` y `servicio_prolongado`; reglas declarativas
   aplican `issubset` y conservan premisas cumplidas/faltantes.
4. **Método secuencial:** el AFD POD valida `A → V → F`; las secuencias son
   pruebas controladas porque Amazon no registra esos eventos.
5. **Trazabilidad:** cada salida identifica si proviene de una fila Amazon, de
   una estadística calculada o de una decisión explícita del
   proyecto. No hay entrenamiento, objetivo ni partición train/test.

### Criterios de validación

- **Realizado:** core, pruebas, informe, evidencia, API y laboratorio Órbita.
- **Funciona:** procesamiento determinista de 14.411 filas y trazas completas.
- **Coincide:** las tres representaciones usan el dominio logístico y el AFD
  acepta `AVF` mientras rechaza `AVC`, `AF` y `AV`.

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
| Infraestructura nueva (cerrada) | PostgreSQL + SQLAlchemy + Alembic + FastAPI; preservar Semanas 2–7 | Migraciones, seeds y API probados sin regresiones históricas |
| Alcance del piloto visual (cerrada) | 200 imágenes sintéticas; asociación simulada a 200 paradas persistida | Fuente Kaggle v2, 200 vistas laterales / grupos, balance 100/100 y manifiesto auditado |
| Tarea visual y MLP | Candidata: clasificación intacto/dañado; arquitectura y preprocesamiento pendientes | Confirmación con guía de Semana 8; no confundir con riesgo tabular |
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

## Dashboard actual y propuesta MLP

La navegación, el resumen y la inspección de datos e imágenes están implementados.
La ficha MLP es provisional y se ajustará con la guía cuando esté disponible.

### 1. Punto de partida real

- React/Vite y FastAPI funcionan como un único monolito.
- La navegación organiza el resumen, los datos y las Semanas 2, 3, 4, 5 y 7 por cortes.
- Cada tema conserva su laboratorio, código explicado e informe.
- La BD contiene 14.411 paradas Amazon y un piloto de 200 imágenes asociadas
  de forma simulada a 200 paradas distintas.
- El piloto tiene endpoints de lectura y pantallas de inspección. No hay MLP visual entrenado.
- Los módulos históricos siguen usando sus fuentes anteriores; no se migran
  a PostgreSQL como parte de un rediseño visual.

### 2. Objetivo del dashboard

Mostrar qué problema resuelve cada módulo, con qué datos, cómo funciona y qué
resultado produce, sin confundir una demostración con evidencia de una entrega
real. Mantener la navegación por cortes y evitar crear una pantalla por archivo.

#### Navegación implementada

```text
Órbita
├── Resumen del proyecto
├── Datos e inspección
│   ├── Paradas Amazon
│   └── Piloto visual simulado
├── Corte 1
│   ├── Semana 2 · Riesgo de retraso
│   ├── Semana 3 · Reglas simbólicas
│   ├── Semana 4 · Búsqueda de rutas
│   └── Semana 5 · Sistema híbrido
├── Corte 2
│   ├── Semana 7 · Representaciones
│   └── MLP visual · propuesta, pendiente de la guía
└── Corte 3 · sin anticipar actividades
```

No reemplazar las vistas existentes ni añadir botones que aparenten ejecutar
algoritmos todavía no implementados.

### 3. Pantallas y estado

| Pantalla | Qué muestra | Estado |
|---|---|---|
| Resumen | Objetivo, módulos disponibles y estado real de datos/servicios | Implementado con datos consultados; la BD indisponible tiene estado explícito |
| Paradas Amazon | Tabla paginada, filtros por ruta/estación y asociación | Implementado; unidades y procedencia explícitas |
| Inspección visual | Imagen, etiqueta de origen, grupo, fuente y parada asociada | Implementado con archivos por ID y aviso permanente de simulación |
| Laboratorio por semana | Problema → datos → ejecución → resultado → explicación → evidencia | Vistas históricas conservadas; ajustar con su guía cuando aplique |
| MLP visual (propuesto) | Ficha de datos y flujo candidato; evaluación y predicción vacías | Ficha implementada; tarea, preprocesamiento y modelo pendientes de guía |

**Ejemplo de flujo de inspección:** seleccionar parada → consultar si tiene
asociación → mostrar imagen y etiqueta → explicar procedencia y limitaciones.
La ausencia de imagen es un estado normal: 14.211 paradas no tienen asociación.

El aviso será visible junto a la imagen, no escondido en una ayuda:

> Imagen sintética asociada aleatoriamente para demostración.
> No corresponde al envío original de Amazon.

Separar siempre **etiqueta de origen**, **predicción futura del modelo** y
**riesgo logístico de retraso**. No usar identificadores ni variables Amazon
como entradas del clasificador visual.

### 4. Estructura común de los laboratorios

1. **Qué hacemos:** objetivo en lenguaje sencillo y actividad de la guía.
2. **Con qué datos:** fuente, cantidad, unidad de observación y limitaciones.
3. **Cómo funciona:** explicación breve; código detallado como consulta opcional.
4. **Probar:** controles permitidos por la actividad, con valores y unidades claros.
5. **Resultado:** métricas con interpretación y evidencia, no solo números.
6. **Informe:** reporte reproducible y vínculo al requisito que cumple.

Mantener estados de carga, vacío, error y BD no disponible. Un fallo de los
módulos nuevos no debe inutilizar las semanas anteriores. Considerar teclado,
contraste, pantallas pequeñas y explicaciones de siglas antes de aprobar UI.

### 5. MLP visual: propuesta básica

**Objetivo provisional:** clasificar el estado **visible** de un empaque
sintético como `intacto` o `dañado`. No inferir daños al contenido ni al envío
Amazon. Las 200 imágenes disponibles (100/100) sirven para un ejercicio
académico pequeño; no permiten prometer rendimiento en fotografías reales.

Una sola pantalla, sin mezclarla con el detalle logístico:

```text
MLP visual
├── Datos: 200 imágenes, clases 100/100, 200 grupos; fuente y límites
├── Método: imagen → preparación → vector de píxeles → MLP → clase
├── Evaluación: particiones, matriz de confusión y métricas con explicación
└── Ejemplo: elegir una imagen del conjunto reservado → ver etiqueta y predicción
```

**Interacción mínima útil:** elegir una imagen del conjunto de evaluación
reservado y ver, lado a lado, su etiqueta de origen y la predicción guardada
del modelo. Mostrar versión del modelo y si acertó. Si se presenta una
probabilidad, identificarla como salida del modelo, **no como certeza de daño
real**. No habilitar subida pública de imágenes ni entrenamiento desde el
navegador en esta primera versión. El entrenamiento se ejecutaría por comando
y la pantalla leería resultados persistidos; si no existe modelo, mostrar
«Aún no entrenado» y nunca una predicción inventada.

**Candidato técnico, no decisión cerrada:** usar un MLP pequeño sobre una
representación reducida de los píxeles, por ejemplo 32×32 en escala de grises
con una capa oculta de 32 neuronas. Así se puede explicar visualmente el paso
de matriz a vector y la salida binaria sin añadir otra arquitectura. Tamaño,
color, número de capas, regularización y librería se confirman con la guía y
una prueba de viabilidad: reducir la imagen podría ocultar deformaciones.
scikit-learn ya es dependencia del proyecto; su [guía oficial de MLP](https://scikit-learn.org/stable/modules/neural_networks_supervised.html)
recomienda escalar las entradas y ajustar cualquier transformación aprendida
solo con entrenamiento. Esta propuesta **no fija** todavía esos parámetros.

**Evaluación honesta:** separar por grupo visual antes de entrenar, mantener
una prueba final sin usarla para escoger parámetros y mostrar al menos matriz
de confusión y métricas por clase, además del número de imágenes de cada
partición. El reparto exacto depende de la guía. Evitar elegir únicamente
ejemplos correctos para el demo. Como las asociaciones Amazon son aleatorias,
la pantalla MLP no debe insinuar relación con retraso, ruta o estación.

**Orden de implementación restante, sujeto a la guía:** la ficha de datos ya
existe; después vendrían el entrenamiento/evaluación reproducibles y, al final,
los resultados y ejemplos en el dashboard. Sin modelo válido, la sección de
predicciones permanece vacía.

### 6. Qué decidir cuando llegue la guía

Crear la matriz a partir del texto real; no completar requisitos por intuición:

| Requisito y referencia exacta | Obligatorio/opcional | Dato/algoritmo | Pantalla o evidencia | Prueba de aceptación | Estado |
|---|---|---|---|---|---|
| Pendiente de recibir guía | Por determinar | Por determinar | Por determinar | Por determinar | No implementado |

Resolver explícitamente: tarea, entradas/salidas, algoritmos permitidos,
preprocesamiento, particiones por grupo, métricas exigidas, entregables y
criterios de evaluación. Solo entonces fijar arquitectura del MLP, tamaños,
entrenamiento e interfaz de resultados. No prometer precisión ni asumir que
un dataset sintético representa fotografías reales de entregas.

### 7. Secuencia acordada

1. **Ahora:** persistencia, API de lectura e interfaz de inspección disponibles;
   contratos publicados con OpenAPI en `/docs`, sin Docusaurus.
2. **Al recibir la guía:** leerla, completar la matriz y detectar brechas frente
   a lo existente; acordar ajustes y realizar la actividad académica por incrementos.
3. **Al terminar la actividad:** ajustar de forma integral dashboard, API,
   documentación y pruebas según el resultado real; sin entrenamiento automático
   al iniciar HTTP.

Cierre de cada incremento: evidencia de pruebas, revisión del usuario y estado
actualizado en la [guía técnica](guia-tecnica.md).
