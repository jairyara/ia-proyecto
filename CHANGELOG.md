# Changelog

Registro de cambios inspirado en
[Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/). El versionado
aplica a las entregas de los cortes 1, 2 y 3.

## [En curso]

### Nomenclatura por temas

- **Sesión 3** (2026-08-21):
  - `refactor` Módulos, pruebas y reportes renombrados por tema
    (`pipeline_iris`, `clasificador_requerimientos`,
    `clasificacion-casos-base`, `clasificacion-requerimientos-logistica`);
    las semanas quedan solo como roadmap en `PLAN-PROYECTO.md`.
  - `docs` Convención de commits por módulo y README reencuadrado por temas.

### Pipeline supervisado de referencia

- **Nivelación** (2026-08-20):
  - `feat` Pipeline reproducible Iris con partición estratificada, escalado y
    regresión logística; accuracy 0.921 y matriz de confusión verificadas.
  - `test` Prueba de tamaños, accuracy y matriz esperada.
  - `docs` Reporte técnico de la práctica en `reports/pipeline-iris.md`.

### Taxonomía y línea base simbólica

- **Sesión 2** (2026-08-20):
  - `chore` Inicialización del repositorio, estructura base, dependencias,
    reglas de contribución y documentación de entrada.
  - `feat` Taxonomía logística y clasificador simbólico reproducible en
    `src/clasificador_requerimientos.py`, con evidencia de las reglas
    activadas.
  - `test` Pruebas de normalización, clasificación multiárea, validación de CSV,
    consistencia de datos y generación del reporte.
  - `docs` Plan de fases, mapeo de áreas de IA y reporte de la taxonomía.
  - `fix` Alineación con las fuentes originales: Python 3.13.x, 20 casos base
    obligatorios, 20 casos logísticos, cinco reglas propias diferenciadas y
    justificación oficial preservada en `docs/`.
  - `chore` Publicación del repositorio privado en GitHub e invitación de
    colaboración con permiso de escritura enviada a `CatherinneG`.

<!-- Plantilla de entrega:
## [v1.0.0] - Corte 1 - AAAA-MM-DD
Resumen verificable de la entrega.
-->
