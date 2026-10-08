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

## Forma de trabajo y continuidad

El planificador híbrido de la [justificación oficial](justificacion-proyecto-08.pdf)
es el **hilo conductor del semestre**, no una orden de integrar todos sus
componentes antes de abordar el siguiente tema. Se trabaja **semana a semana**:
cada guía se adapta al dominio logístico como un módulo verificable por sí mismo
y se presenta en Órbita. La integración entre módulos avanza de forma
acumulativa cuando el contenido del curso y el corte correspondiente la exijan.

| Capa | Estado comprobable | Papel |
|---|---|---|
| Búsqueda, riesgo y reglas de Semanas 2–5 | Implementados y probados como prácticas separadas | Módulos del proyecto |
| Representaciones de Semana 7 | Implementadas y probadas | Módulo del proyecto |
| Datos Amazon, PostgreSQL y API de inspección | Implementados | Infraestructura y datos |
| Imágenes, MLP y GraphML de Semana 8 | Experimento reproducible; MLP 0,48 frente a baseline 0,50 | Práctica de reconocimiento presentada en Órbita; **no** automatización operativa |
| Canny, Otsu y regiones de Semana 9 | Escena sintética propia de un paquete, CLI y evidencia versionada | Preparación visual didáctica; **no** detector de daños ni conteo operativo de bultos |
| Regiones, intensidad y LBP de Semana 10 | 150 imágenes auditadas de entrenamiento, vector 53D y comparación por clase | Descripción exploratoria; la banda domina parte de la máscara y **no** valida detección de daños |
| Integración de una jornada completa | Aún no hay orquestador ni prueba extremo a extremo | Objetivo acumulativo de cortes posteriores, no tarea que desplace la guía semanal |

**Ciclo de trabajo por semana:**

1. Leer la guía oficial y delimitar qué enseña, qué exige y cómo se relaciona
   con el problema logístico; no inventar requisitos de semanas futuras.
2. Implementar el tema como módulo aislado en `src/`, reutilizando contratos o
   datos existentes solo cuando aporten a esa práctica.
3. Añadir pruebas y un informe reproducible en `reports/sem-NN-*.md` con
   método, resultados reales, límites y correspondencia con la guía.
4. Exponer el mismo módulo mediante `api/` y su vista de Semana NN en Órbita,
   respetando **Laboratorio / Código explicado / Informe** y sin alterar
   laboratorios anteriores.
5. Cerrar la semana contra la **rúbrica**, no contra los nombres de archivo o
   tecnologías del ejemplo: documentar objetivo, adaptación, motivo y evidencia.
   Integrar con otros módulos cuando el corte lo requiera, en un cambio separado.

**Siguiente paso:** contrastar cada práctica con su rúbrica y conservar sus
límites. Semanas 9 y 10 se documentan en [`reports/semana09.md`](../reports/semana09.md)
y [`reports/semana10.md`](../reports/semana10.md), sin asociar imágenes a
envíos Amazon observados ni activar decisiones de despacho.

**Regla de orden:** `docs/proyecto.md` decide alcance y prioridades;
`docs/guia-tecnica.md` explica operación; `reports/` conserva resultados;
`docs/plan-semana-08.md` registra el plan y límites de esa práctica. Los datos,
manifiestos, migraciones aplicadas y evidencia reproducible no se borran para
simular una limpieza. Archivos generados e ignorados por Git se regeneran o se
limpian solo cuando no sean necesarios para la BD y la operación local.

### Qué significa «piloto» en Semana 8

| Pieza | Para qué se añadió | Qué **no** demuestra |
|---|---|---|
| 200 imágenes sintéticas auditadas | Tener un conjunto visual etiquetado del dominio para la práctica de reconocimiento | Que correspondan a paquetes o entregas Amazon reales |
| 200 asociaciones aleatorias imagen–parada | Demostrar persistencia y navegación entre registros logísticos y visuales | Relación física observada ni característica usada por el MLP |
| Experimento MLP | Entrenar con 150 imágenes (75 %) y evaluar con 50 reservadas (25 %), sin cruzar grupos | Capacidad de decidir despachos: 0,48 queda por debajo de la línea base 0,50 |

Los tres elementos se presentan separados en Órbita. El 75/25 pertenece **al
experimento MLP**, no al reparto de asociaciones con Amazon. La evaluación se
realiza solo sobre el 25 % reservado; «entrenamiento» no significa uso
operativo del modelo.

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
- [x] API e interfaz de inspección, con OpenAPI en `/docs`.
- [x] Semana 8: MLP visual evaluado, evidencia PostgreSQL y ontología GraphML.
  Accuracy de prueba **0,48**, inferior a la línea base **0,50**; uso solo didáctico.
- [x] Semana 9: Canny, Otsu y regiones sobre escena dibujada, sin diagnóstico.
- [x] Semana 10: extracción descriptiva 53D sobre 150 imágenes sintéticas auditadas;
  50 casos de prueba permanecen reservados y no hay clasificador nuevo.

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

Cerrar el [módulo de Semana 8](../reports/sem-08-reconocimiento.md) contra su
rúbrica con una matriz de equivalencias y justificaciones; **no** agregar SQLite
ni otro ejemplo genérico solo para copiar la presentación. El resultado del MLP
no justifica automatizar decisiones de despacho.
Continuar con la próxima guía mediante el [ciclo semanal](#forma-de-trabajo-y-continuidad).
La jornada extremo a extremo permanece como meta de integración por cortes,
sin reemplazar las prácticas semanales. CI consolidada sigue pendiente.

Trabajar por incrementos revisables con pruebas y confirmación del usuario;
no migrar retroactivamente las entregas académicas anteriores.

## Roadmap

Material confirmado del curso hasta la **Semana 10**. Las semanas posteriores se actualizan según se publique el material.

| Semana | Contenido oficial | Aplicación al proyecto logístico | Estado |
|---:|---|---|---|
| **2** | Fundamentos y entorno | Repositorio reproducible y baseline predictivo (`src.modelado.riesgo_retraso`) | **Completado** |
| **3** | Taxonomía de IA | Mapeo de 7 áreas y clasificador simbólico (`src.clasificacion.requerimientos`) | **Completado** |
| **4** | Marco tecnológico y búsqueda | Grafo vial, A* con heurística admisible Haversine, línea base no informada y replanificación (`src.busqueda`) | **Completado** |
| **5** | Marco tecnológico: sistemas híbridos | Reglas expertas + TF-IDF/coseno + regresión logística con trazabilidad, demostrable en el dashboard (`src.hibrido`) | **Completado** |
| 6 | Entrega Corte 1 | Tag `v1.0.0` y módulos demostrables; la jornada integrada sigue pendiente | **Entrega académica completada; integración de producto pendiente** |
| **6** | **Corte 1** | **Planifica rutas — `v1.0.0`** | **Meta hito** |
| **7** | Representaciones del reconocimiento | Vectores Amazon, euclidiana/IQR, hechos P75 y AFD POD (`src.representaciones`) | **Completado** |
| Pre-8 | Hito técnico acordado por el equipo, no actividad oficial adicional | BD, migraciones, seed Amazon, piloto visual sintético y dashboard de inspección | **Completado** |
| **8** | Redes neuronales, base de imágenes y ontologías | MLP sobre piloto de 200 imágenes, evidencia PostgreSQL y GraphML; resultado inferior a baseline, solo didáctico | **Implementado y evaluado** |
| **9** | Características, contornos y segmentación | Canny, Otsu y regiones en una escena logística sintética | **Implementado y evaluado** |
| **10** | Segmentación por histogramas, regiones y texturas | Descriptor 53D sobre imágenes auditadas, con comparación descriptiva y límites explícitos | **Implementado y evaluado** |
| 11–12 | Materiales pendientes | Alcance sujeto a guías oficiales; motor de restricciones y conocimiento siguen como objetivos del corte | Pendiente |
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
| Tarea visual y MLP (cerrada para el piloto) | Clasificación intacto/dañado con gris 16×16 y MLP de 64 neuronas | Evaluación 150/50 por grupo y límites documentados; no confundir con riesgo tabular |
| Adaptación de la guía (cerrada) | Dataset de paquetes, PostgreSQL, almacenamiento visual privado y Python 3.14 | Explicar equivalencia funcional y evidencia frente a los ejemplos de clase |
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

## Dashboard y Semana 8

Órbita conserva las vistas de Semanas 2–7, la entrada histórica y las pestañas
**Laboratorio / Código explicado / Informe**. Se añadió Semana 8 al Corte 2:
consulta el modelo evaluado, la matriz de confusión, una predicción de prueba
persistida y el recorrido semántico. La API FastAPI sigue documentada en
`/docs`; no se agregó otra API ni Docusaurus.

El experimento es reproducible con `python -m src.semana08_reconocimiento
--registrar` tras `python -m alembic upgrade head`. Usa las 200 imágenes
sintéticas `side`, separadas 150/50 por grupo, gris 16×16 y MLP de 64 neuronas.
En prueba obtuvo **accuracy 0,48**, frente a **0,50** del clasificador
mayoritario, con advertencia de no convergencia. Por ello se muestra como
aprendizaje y trazabilidad, **no** como decisión automática de despacho. Las
asociaciones con paradas Amazon siguen siendo simuladas.

La evidencia queda en `modelos_visuales` y `muestras_modelo_visual`, sin cambiar
la etiqueta de origen de `imagenes`; el grafo dirigido se exporta a GraphML
con la relación de un caso concreto. Consulta el [plan de Semana 8](plan-semana-08.md),
el [informe de resultados](../reports/sem-08-reconocimiento.md) y la
[guía técnica](guia-tecnica.md) para reproducción y límites.

**Decisión de adaptación:** el ejemplo `load_digits` + SQLite de clase se
reemplaza por imágenes de paquetes y PostgreSQL, que ya es la base operativa.
No se añadirá una segunda base ni se duplicará el experimento para reproducir
nombres de archivo. El informe debe justificar explícitamente la equivalencia
frente a la rúbrica.
