# Changelog

Registro de cambios inspirado en
[Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/). El versionado
aplica a las entregas de los cortes 1, 2 y 3.

## [En curso]

- **docs** (2026-09-23): actualiza el estado del dashboard y de la API visual;
  OpenAPI en `/docs` es suficiente por ahora. La revisión integral se hará al
  terminar la actividad de Semana 8 con su guía, sin añadir Docusaurus.
- **feat** (2026-09-23): agrega resumen, inspección paginada de paradas e imágenes,
  archivos visuales por ID y ficha MLP sin predicciones; conserva los laboratorios.

- **docs** (2026-09-23): consolida las guías de transición en
  `docs/guia-tecnica.md` (estado actual y operación) y `docs/proyecto.md`
  (alcance académico y dashboard propuesto). Retira los documentos por fases,
  investigación separada, índice redundante y referencias dispersas en raíz;
  conserva manifiestos de procedencia, reportes académicos y comandos vigentes.

- **chore** (2026-09-23): ordena el repositorio sin retirar código, datos ni evidencia
  académica; elimina marcadores vacíos sin uso y metadatos/cachés propios.
  - `docs` Índice de documentación y enlace roto del README corregido.
  - `docs` Sustituye el plan inicial del dashboard por una propuesta basada en
    el estado actual; implementación y requisitos pendientes de la guía.
  - `chore` Verifica un único proyecto Compose con app + PostgreSQL healthy,
    conservando los volúmenes de BD e imágenes; no modifica otros proyectos.

- **feat** (2026-09-23): cierra fase 4, piloto visual persistido, sin API/interfaz ni MLP.
  - `feat` Migración 0003 con imágenes, pilotos y asociaciones; FK compuestas,
    unicidad por piloto y conservación íntegra de datos Amazon.
  - `feat` Mapa versionado de 200 asociaciones simuladas, algoritmo y semillas
    independientes; hashes de ambos orígenes y del mapa.
  - `feat` CLI con dry-run, auditoría, staging y publicación por lote; reintentos,
    concurrencia, versionado y detección de corrupción sin sobrescrituras.
  - `chore` Volumen visual persistente fuera de la SPA; piloto real importado y
    segunda ejecución sin cambios, conservado tras recrear el monolito.
  - `test` 160 pruebas con PostgreSQL real, local y Docker; 135 aprobadas/25 omitidas sin
    BD, 17 frontend y builds correctos; fuentes reales y volumen verificados.
  - `docs` Guía de fase 4, mapa reproducible, operación, recuperación y límites.

- **feat** (2026-09-22): cierra fase 3 del piloto visual, sin adelantar persistencia
  de imágenes, asociaciones, API/interfaz nueva ni entrenamiento.
  - `feat` Fuente Industrial Quality Control of Packages v2 (GPL 2 declarada):
    200 vistas laterales originales, 100 intactas/100 dañadas, 200 seriales/grupos,
    PNG RGB 960×540 y 126.285.817 bytes. Originales excluidos de Git y Docker.
  - `feat` Adquisición selectiva/reanudable, `--dry-run` sin red y auditoría offline;
    manifiesto con procedencia, tamaños y hashes de bytes/píxeles. Repetición
    idempotente y validación de rutas, formato, etiquetas, grupos y duplicados.
  - `test` 139 pruebas backend aprobadas con PostgreSQL real, local y Docker;
    126 aprobadas/13 omitidas sin BD; 17 frontend y builds correctos. Auditoría
    real de los 200 originales y revisión visual con límites explícitos.
  - `docs` Guía de fase 3, investigación primaria y evidencia de licencia;
    un solo diseño de empaque/escenario, sin afirmar generalización a Amazon.

- **fix** (2026-09-22): restaura acceso al monolito Docker por localhost:8000;
  el contenedor smoke sin red/puertos había quedado activo en vez de la app real.
  - `chore` Un único proyecto Compose `ia-proyecto` con dashboard + PostgreSQL;
    puerto web configurable, puertos locales y logs rotados. `.env.example`
    activa el perfil de persistencia para arrancar ambos con un comando.
  - `docs` Arranque, verificación y parada documentados; operaciones de BD por
    `exec`, contenedores administrativos temporales con `run --rm`.
  - `chore` Eliminados exclusivamente smoke y contenedores/redes/volúmenes
    desechables de fases 1–2; se preservan los proyectos ajenos.

- **feat** (2026-09-22): cierra fase 2 de datos Amazon sin modificar Semanas 2–7.
  - `feat` Migración `0002_datasets_logistica`, modelos versionados, auditoría,
    estaciones, rutas y paradas; integridad entre datasets y decimales exactos.
  - `feat` Manifiesto SHA-256 y CLI `python -m src.datos.seed`, con `--dry-run`,
    validación estricta, carga atómica, versiones inmutables e idempotencia
    incluso con ejecuciones simultáneas. Lectura interna paginada con filtros.
  - `test` 122 pruebas backend aprobadas localmente y en Docker con PostgreSQL
    real; 109 aprobadas y 13 omitidas explícitamente sin BD. Comparación de las
    20 columnas de 14.411 paradas, 100 rutas y 17 estaciones; rollback y reintento.
    17 pruebas frontend y builds frontend/Docker correctos.
  - `docs` Guía `docs/guia-tecnica.md`, README y estado del plan actualizados.
    Fuente visual, API/interfaz nueva y MLP permanecen pendientes.

- **feat** (2026-09-22): cierra fase 1 de infraestructura persistente, sin
  modificar los módulos académicos de Semanas 2–7.
  - `chore` Python 3.14 como versión elegida en entorno, Docker y documentación;
    PostgreSQL 17.11 con perfil Compose opcional, volumen y puerto local.
  - `feat` Configuración diferida, base SQLAlchemy, motor y sesiones con
    transacciones explícitas; Alembic con revisión inicial `0001_base`.
  - `test` 100 pruebas backend aprobadas en Docker con PostgreSQL real;
    sin BD/red, 98 aprobadas y 2 omitidas explícitamente. 17 pruebas frontend,
    build frontend y build Docker aprobados. Migración conservada tras reinicio.
  - `test` Health, búsqueda, modelado, representaciones y SPA responden HTTP 200
    en un contenedor sin red ni BD; 20 casos del clasificador sin discrepancias.
  - `docs` Guía `docs/guia-tecnica.md`, evidencia de cierre y plan
    actualizado. Tablas logísticas y seed reservados para fase 2; sin imágenes
    ni entrenamiento en esta entrega.

- **docs** (2026-09-22): simplifica el piloto a una fuente sintética pequeña y
  etiquetada; Parcel3D deja de ser obligatorio. Define ejecución fase a fase con
  estado, entregables, pruebas y revisión antes de continuar. Mantiene las 200
  imágenes y asociaciones simuladas; no descarga ni genera datos todavía.

- **docs** (2026-09-22): define el plan de arquitectura incremental y piloto
  Parcel3D de 200 imágenes asociadas a 200 pedidos de forma aleatoria,
  reproducible y explícitamente simulada. Conserva Semanas 2–7 y deja el MLP
  pendiente de la guía; no incorpora todavía BD, imágenes ni entrenamiento.

### Semana 07 — Representaciones del reconocimiento (`src/representaciones/`)

- **feat** (2026-09-17): aplicación trazable al Proyecto 8.
  - `feat` Procesamiento de 14.411 paradas reales Amazon con vector
    `[distancia, volumen, servicio]`, referencia mediana, escala IQR y distancia
    euclidiana cruda/normalizada; no hay entrenamiento ni partición train/test.
  - `feat` Traducción Numérico ↔ Simbólico mediante percentiles 75 calculados,
    tres reglas didácticas auditables y AFD POD con escenarios controlados.
  - `feat` API `/api/representaciones/contexto` y
    `/api/representaciones/evaluar`, además del laboratorio Semana 07 dentro de
    Corte 2 con procedencia visible para cada salida.
  - `docs` Informe `reports/sem-07-representaciones.md` y evidencia regenerable.
  - `test` Pruebas de estadísticas, límites P75, reglas,
    autómatas, procedencia y contratos de dashboard.
  - `fix` La entrega conserva solo la adaptación logística, muestra las tres
    salidas en consola y comparte los escenarios POD entre API y dashboard.

### Dashboard interactivo y didáctico de IA (`api/`, `dashboard/`)

- **feat** (2026-09-08): ampliación didáctica de la Semana 5.
  - `feat` El laboratorio ofrece 8 consultas de demostración: conserva las 3
    de la guía y añade casos para ventanas horarias, prioridad, destinatario
    ausente, mercancía frágil y activación simultánea de dos reglas.
  - `feat` La categoría operativa diferencia las probabilidades de salida de
    los tres términos con mayor aporte local positivo (`peso × TF-IDF`).
  - `fix` El clasificador se abstiene con `Requiere revisión` cuando la consulta
    no contiene vocabulario conocido o las dos clases principales quedan casi
    empatadas, en vez de forzar una categoría con probabilidades uniformes.
  - `test` Se validan 73 pruebas Python, 15 pruebas frontend y el build de
    producción con pnpm.
- **style** (2026-09-08): control del menú lateral integrado al contenido.
  - `style` El botón circular superpuesto a la marca Órbita se reemplaza por un
    control rectangular con icono de panel lateral dentro del header compartido.
  - `a11y` Conserva etiquetas dinámicas, `aria-controls` y `aria-expanded`; en
    móvil se mantiene el control independiente del menú.
- **feat** (2026-09-06): interfaz optimizada para sustentación en TV 4K.
  - `feat` El menú lateral se puede contraer a una barra de iconos para ampliar
    el laboratorio; el estado se conserva en el navegador y cada acceso mantiene
    etiqueta accesible y ayuda contextual.
  - `style` La interfaz aplica escalado proporcional automático en viewports 2K
    y 4K, eleva a 11 px el mínimo tipográfico y refuerza tamaños/contraste de
    texto, código, tablas y controles sin alterar el menú móvil.
  - `fix` El estado colapsado se aplica directamente al aside para ocultar sin
    recortes la marca, textos y estado de API incluso con escalado del sistema.
  - `test` Se valida la interacción accesible y el mínimo tipográfico; 7 pruebas
    frontend y el build de producción pasan con pnpm.
- **feat** (2026-09-03): Semana 5 — sistema híbrido trazable demostrable en el dashboard.
  - `feat` Motor híbrido en `src/hibrido/sistema.py`: 5 reglas expertas del
    dominio logístico declaradas como datos (`Regla(accion, palabras,
    descripcion)`) que reportan la palabra detonante de cada disparo,
    recuperación documental con `TfidfVectorizer` + similitud coseno sobre
    `data/base_conocimiento.txt` (10 protocolos SOP) y clasificación
    supervisada `LogisticRegression` (16 ejemplos, 4 clases operativas) con
    distribución de probabilidad completa.
  - `feat` Script reproducible `python -m src.sistema_hibrido` que ejecuta las
    3 consultas de la guía y genera `reports/sem-05-sistema-hibrido-evidencia.md`.
  - `feat` API `/api/hibrido/responder` (trazabilidad: reglas + detonantes,
    evidencia + similitud, clase + probabilidades) y `/api/hibrido/contexto`
    (reglas, clases, consultas de ejemplo y base documental).
  - `feat` Laboratorio Semana 5 en el dashboard: consulta en lenguaje natural
    con presets de la guía, clase predicha con barras de probabilidad,
    trazabilidad en tres nodos (regla + detonante → protocolo + similitud →
    clase) y catálogo visual de las 5 reglas expertas; pestañas **Código
    explicado** e **Informe** habilitadas con el catálogo actualizado.
  - `docs` Reporte técnico `reports/sem-05-sistema-hibrido.md` con arquitectura,
    base de conocimiento, reglas, evidencia de ejecución, limitaciones y
    conexión con el Corte 2.
  - `test` 12 pruebas nuevas del motor y 2 de integración de servicios; 67/67
    pruebas Python pasan.
- **feat** (2026-09-01): apertura del IDE desde el modo de lectura.
  - `feat` El explorador permite elegir PyCharm o VS Code y abrir el archivo
    real directamente en la línea seleccionada mediante enlaces locales
    `pycharm://` y `vscode://`.
  - `config` Docker Compose comunica al frontend la ruta del repositorio en el
    host para evitar que el IDE intente abrir la ruta interna `/app`.
  - `test` Se validan la construcción segura de enlaces, la línea activa y el
    rechazo de rutas que intenten salir del repositorio.
- **feat** (2026-09-01): workspace semanal de aprendizaje y migración a pnpm.
  - `feat` Navegación lateral ascendente (Semana 2, 3, 4) y pestañas compartidas
    **Laboratorio**, **Código explicado** e **Informe** para cada semana.
  - `feat` Catálogo backend con allowlist, lectura del código Python real,
    estructura AST y explicación interactiva de todas sus líneas; las trazas de
    A*, Dijkstra y BFS usan ahora los números de línea originales.
  - `feat` Visualizador de reportes Markdown con tabla de contenido, búsqueda,
    fuente cruda, GFM y fórmulas KaTeX.
  - `config` Sustitución completa de npm por `pnpm@11.25.0`, lockfile congelado,
    Corepack en Docker y comandos pnpm documentados.
  - `test` Pruebas de catálogo seguro, trazas por rango AST, interacción del
    explorador y renderizado Markdown; 55 pruebas Python y 2 frontend pasan.
- **feat** (2026-09-01): implementación de **Órbita**, dashboard de sustentación.
  - `feat` API FastAPI con contratos Pydantic para trazas compactas de A*,
    Dijkstra y BFS, replanificación, inferencia supervisada y clasificación
    simbólica.
  - `feat` SPA React/Vite/Tailwind accesible y responsiva con reproductor paso a
    paso, cuadrícula SVG interactiva, grafo Amazon, panel de código sincronizado,
    métricas comparativas, simulador de pedidos y árbol de reglas.
  - `architecture` La trazabilidad vive en `api/services/` como proyección
    didáctica; los resultados canónicos continúan en `src/` sin cambios de API.
  - `chore` Empaquetado multi-stage y ejecución unificada mediante
    `docker compose up --build`.
  - `test` Se agregan pruebas de integración de servicios; 50/50 pruebas Python
    pasan y el frontend compila para producción.

### Renombrado de reportes con consecutivo por semana (`reports/`)

- **docs** (2026-08-28): los reportes pasan de `<tema>.md` a `sem-XX-<tema>.md`
  (`sem-02-riesgo-retraso.md`, `sem-02-datos-amazon-last-mile.md`,
  `sem-03-taxonomia-ia.md`, `sem-03-clasificacion-requerimientos.md` y
  `sem-04-busqueda-rutas.md`) para identificar la semana de cada tema.
  Se actualizan las rutas por defecto de los generadores (`src/datos/amazon.py`,
  `src/modelado/riesgo_retraso.py`, `src/clasificacion/requerimientos.py`,
  `src/busqueda_rutas.py`) y las referencias en `docs/proyecto.md` y
  `CONTRIBUTING.md`. Se elimina `src/busqueda/replanificar_script.py`, duplicado
  sin uso de `src/busqueda_rutas.py`.

### Búsqueda heurística A*, líneas base y replanificación (`src/busqueda/`)

- **feat** (2026-08-28): implementación completa del módulo de búsqueda para el Corte 1.
  - `feat` Se implementa `GrafoEntregas` (`src/busqueda/grafo.py`) con soporte para matrices $N \times N$ de Amazon Last Mile, cuadrículas sintéticas y bloqueo dinámico de vías.
  - `feat` Se implementa búsqueda $A^*$ (`src/busqueda/a_estrella.py`) con heurística geodésica admisible $h(n) = \text{Haversine}/v_{\max}$ y Manhattan.
  - `feat` Se implementan líneas base no informadas Dijkstra y BFS (`src/busqueda/no_informada.py`).
  - `feat` Se implementa ciclo dinámico de replanificación ante vías bloqueadas (`src/busqueda/replanificacion.py`).
  - `feat` Script de benchmarking `src/busqueda_rutas.py` y reporte técnico `reports/sem-04-busqueda-rutas.md` (reducción de hasta 67.3% de exploración con 100% de optimalidad).
  - `test` Se agrega suite `tests/test_busqueda.py`; 45/45 pruebas unitarias pasando.

### Plan de proyecto — Especificación técnica de Semana 4 (Búsqueda y A*)

- **docs** (2026-08-28): integración de temáticas oficiales de la Semana 4.
  - `docs` Se actualiza `docs/proyecto.md` con los materiales oficiales de Downloads
    (`Guia_Explicativa_Semana_04_IA_Estudiantes.pdf` y `Semana_04_Marco_tecnologico_de_la_inteligencia_artificial_Clase.pptx`).
  - `docs` Se formalizan los 5 elementos de búsqueda (Estado, Acción, Transición,
    Meta, Costo) y la heurística geodésica admisible $h(n)$ sobre el grafo de
    rutas de Amazon Last Mile.
  - `docs` Se cierran las decisiones de topología de entrega y fuentes de datos.

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
  - `docs` `reports/sem-02-datos-amazon-last-mile.md` documenta la procedencia, resumen
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
  - `docs` `docs/proyecto.md` registra las decisiones cerradas (tarea y variables)
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
