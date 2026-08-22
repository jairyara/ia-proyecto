# Changelog

Registro de cambios inspirado en
[Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/). El versionado
aplica a las entregas de los cortes 1, 2 y 3.

## [En curso]

### Enfoque en el dominio logístico

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
