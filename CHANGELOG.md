# Changelog

Registro de cambios inspirado en
[Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/). El versionado
aplica a las entregas de los cortes 1, 2 y 3.

## [En curso]

### Arquitectura modular de paquetes y librerías (`src/`)

- **refactor** (2026-08-28): estructuración modular de la base de código.
  - `refactor` Se modulariza `src/` en subpaquetes cohesivos:
    - `src/comun/`: utilidades geodésicas (`geo.py`) y cliente de red con reintentos (`red.py`).
    - `src/datos/`: curaduría de Amazon Last Mile (`amazon.py`) y generador sintético (`sintetico.py`).
    - `src/modelado/`: pipeline de clasificación y evaluación de riesgo de retraso (`riesgo_retraso.py`).
    - `src/clasificacion/`: clasificador determinista y taxonomía de requerimientos (`requerimientos.py`).
  - `feat` Se implementa carga diferida (`__getattr__`) en `__init__.py` de los paquetes para evitar advertencias de `runpy` al ejecutar con `-m`.
  - `refactor` Se conservan accesos directos en la raíz de `src/` (`extraer_datos_amazon.py`, `generador_pedidos.py`, `modelo_riesgo.py`, `clasificador_requerimientos.py`) para 100% retrocompatibilidad.
  - `test` Se agrega `tests/test_comun.py`; 35/35 pruebas unitarias pasan.

### Datos de dominio real — Amazon Last Mile Routing Challenge

- **feat** (2026-08-28): extracción y curaduría de datos reales de Amazon Last Mile.
  - `feat` `src/extraer_datos_amazon.py` descarga vía HTTPS directo desde AWS Open
    Data (`s3://amazon-last-mile-challenges/almrrc2021/`), limpia inconsistencias,
    calcula volúmenes $m^3$, distancias geodésicas Haversine, ventanas horarias,
    secuencias reales y riesgo de retraso, produciendo `data/amazon_pedidos.csv`
    (14,411 paradas/pedidos limpios de 100 rutas estratificadas) y
    `data/amazon_rutas_muestra.json` (13 grafos de rutas con matrices NxN de tiempos).
  - `test` `tests/test_extraer_datos_amazon.py` valida Haversine, estratificación
    por estación, integridad de columnas, normalización de nulos y construcción de grafos (32/32 tests pasan).
  - `docs` `reports/datos-amazon-last-mile.md` documenta la procedencia, resumen
    estadístico por estación y diccionario de variables.

### Baseline supervisado de riesgo de retraso (Corte 1, decisiones cerradas)

- **feat** (2026-08-29): pipeline supervisado reproducible.
  - `feat` `src/generador_pedidos.py` genera `data/pedidos.csv` (800 casos,
    seed 20260828) con distribuciones documentadas: triangular para distancia/volumen,
    uniforme para ventana e índice de tráfico, elección ponderada para prioridad y
    binomial para indicadores; la etiqueta de retraso sigue una regla logística
    con ruido controlado del 10%.
  - `feat` `src/modelo_riesgo.py` compara LogisticRegression y RandomForest con
    partición estratificada 75/25, selecciona por F1 y guarda el artifact en
    `artifacts/`. Métricas del reporte: accuracy 0.8650 y F1 0.7327
    (LogisticRegression) que superan a RandomForest (0.8350 / 0.6374).
  - `test` Cobertura nueva de reproducibilidad, rangos plausible,
    pipeline completo y contenido del reporte.
  - `docs` `PLAN-PROYECTO.md` registra las decisiones cerradas (tarea y variables)
    y queda el seguimiento post-Corte 1 para evaluar el dataset público
    **Amazon Last Mile Routing Challenge**.
- **Feedback recibido** (2026-08-28):
  - `docs` El profesor valora la lógica de dominio (rutas, restricciones,
    última milla, capacidad y replanificación) pero solicita el componente de
    aprendizaje supervisado de la Semana 2 y recuerda el Control IA sobre
    evidencia de agente generador de código en los commits.

- **Limpieza** (2026-08-22):
  - `update` El repositorio se enfoca exclusivamente en el dominio de
    logística y distribución: se retiran el pipeline de nivelación Iris, los
    20 casos base genéricos de la guía y su reporte. El historial de git
    conserva la evidencia de esas prácticas.
  - `refactor` El clasificador usa un único vocabulario del dominio (rutas y
    última milla, demanda y retrasos, restricciones operativas, verificación
    de paquetes, seguimiento de envíos, reparto autónomo); `data/requerimientos_logistica.csv`
    es la entrada por defecto. 20/20 requerimientos coinciden con la
    referencia y las pruebas pasan.

### Taxonomía y línea base simbólica

- **Ampliación de vocabulario** (2026-08-22):
  - `update` Reglas propias ampliadas con vocabulario de mensajería y última
    milla: reparto, volumen y demanda de envíos, tiempos de entrega, código
    de barras, seguimiento y estado del envío, reclamos, y reparto autónomo
    con drones.
- **Sesión 2** (2026-08-20):
  - `chore` Inicialización del repositorio, estructura base, dependencias,
    reglas de contribución y documentación de entrada.
  - `feat` Taxonomía logística y clasificador simbólico reproducible en
    `src/clasificador_requerimientos.py`, con evidencia de las reglas
    activadas.
  - `test` Pruebas de normalización, clasificación multiárea, validación de CSV,
    consistencia de datos y generación del reporte.
  - `docs` Plan de fases, mapeo de áreas de IA y reporte de la taxonomía.
  - `chore` Publicación del repositorio privado en GitHub e invitación de
    colaboración con permiso de escritura enviada a `CatherinneG`.

<!-- Plantilla de entrega:
## [v1.0.0] - Corte 1 - AAAA-MM-DD
Resumen verificable de la entrega.
-->
