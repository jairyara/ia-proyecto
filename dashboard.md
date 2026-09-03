# Plan de Implementación — Dashboard Interactivo y Didáctico de IA

**Proyecto 8 · Inteligencia Artificial · 10.º semestre**
**Equipo:** Jair Yara y Catherinne Gutierrez
**Objetivo:** Desarrollar un dashboard interactivo de sustentación y visualización algorítmica semana a semana que permita **explicar el código bloque a bloque y línea a línea**, sincronizado con la **ejecución reactiva en vivo** de los modelos y algoritmos de IA, manteniendo intacta la estructura y ejecución académica del repositorio.

---

## 1. Visión y Principios de Diseño

1. **Didáctico y Explicable:** Cada vista algorítmica cuenta con un panel tipo IDE que resalta la línea o bloque exacto de código en ejecución, explicando qué variables y estructuras de datos (colas de prioridad, conjuntos abiertos/cerrados, pesos, métricas) se están modificando en cada paso.
2. **Reactivo y en Tiempo Real:** El usuario puede interactuar con el entorno (hacer clic en la cuadrícula para bloquear vías o cambiar coordenadas) y observar cómo el algoritmo responde y replanifica mediante un reproductor React con temporizador controlado. Los cálculos siguen siendo discretos y verificables; no se promete una tasa de cuadros que dependa del equipo del evaluador.
3. **Desacoplamiento Estricto:** La lógica de inteligencia artificial de la materia vive exclusivamente en `src/` en Python puro. La interfaz web (`dashboard/`) y la API HTTP (`api/`) son capas consumidoras que no alteran los módulos académicos ni las pruebas unitarias.
4. **Reproducibilidad Dual (Docker + Consola Local):**
   - El proyecto puede levantarse completamente con un único comando: `docker compose up --build`.
   - Quien no use Docker (como el evaluador por consola) puede seguir ejecutando `source .venv/bin/activate` y `python -m unittest discover tests` con 100% de compatibilidad.

---

## 2. Arquitectura del Sistema

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                          DASHBOARD (Vite + React)                           │
│  ┌───────────────────────────────┐     ┌─────────────────────────────────┐  │
│  │ Laboratorio / Código explicado│     │      Informe Markdown           │  │
│  │ • Fuente real + explicación   │◄───►│ • TOC, búsqueda, GFM y KaTeX    │  │
│  │ • Simulador paso a paso       │     │ • Vista renderizada / fuente    │  │
│  └───────────────────────────────┘     └─────────────────────────────────┘  │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │ HTTP / JSON (REST API)
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                            API (FastAPI + Uvicorn)                          │
│  • Endpoint /api/busqueda/a-estrella/simular                                │
│  • Endpoint /api/busqueda/replanificar                                      │
│  • Endpoint /api/modelado/predecir-riesgo                                   │
│  • Endpoint /api/clasificacion/evaluar-requerimiento                        │
│  • Endpoints /api/hibrido/responder y /api/hibrido/contexto                 │
│  • Endpoints /api/contenido/* (catálogo seguro, código e informes)           │
│  • Servicios de trazabilidad que proyectan el core sin modificarlo           │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │ Importaciones nativas de Python
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                     CORE DE IA (src/ — La Materia)                          │
│  • src.busqueda (GrafoEntregas, a_estrella, dijkstra, replanificacion)     │
│  • src.modelado (Pipeline de riesgo de retraso, LogisticRegression, RF)     │
│  • src.clasificacion (Motor de reglas simbólicas de taxonomía)              │
│  • src.hibrido (Reglas expertas + TF-IDF/coseno + LogisticRegression)       │
│  • src.comun & src.datos (Haversine geodésico, datasets Amazon y sintético) │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Especificación de Vistas por Semana

### Vista Semana 4: Búsqueda Heurística $A^*$, Baselines y Replanificación
* **Selector de Entorno:**
  - **Cuadrícula Sintética 5×5:** Celdas interactivas donde el usuario hace clic para activar/desactivar obstáculos dinámicos en vivo.
  - **Grafo Real Amazon Last Mile:** Visualización geográfica de nodos (paradas con lat/lon) y aristas con matrices reales de tiempo.
* **Selector de Heurística / Algoritmo:**
  - $A^*$ con Manhattan (para cuadrícula).
  - $A^*$ con Haversine $/ v_{\max}$ (para grafos GPS reales de Amazon).
  - $A^*$ con Euclidiana.
  - Dijkstra ($h=0$, Búsqueda no informada de costo uniforme).
  - BFS (Búsqueda no informada por niveles).
* **Controles de Reproducción:**
  - Botones `Play`, `Pausa`, `Paso Anterior`, `Paso Siguiente`, `Reiniciar`.
  - Slider de velocidad de animación (1x, 2x, 5x, 10x).
* **Panel de Código Sincronizado:**
  - Muestra el fragmento de código de `a_estrella.py`.
  - Resalta en tiempo real la línea activa (ej. `heapq.heappop`, `costo_g + arista`, `if vecino not in g_score`).
  - Muestra el contenido actual del `open_set` (cola de prioridad) con valores $(f, g, h)$ de cada candidato.
* **Métricas en Vivo:**
  - Costo acumulado $g(\text{actual})$, Nodos expandidos, Nodos en frontera, Tiempo de cómputo estimado y comparativa vs Dijkstra.
* **Evento Dinámico de Replanificación:**
  - Botón "Bloquear tramo actual" para simular una vía cerrada en plena ejecución y ver cómo el algoritmo recalcula la ruta óptima instantáneamente.

### Vista Semana 2: Aprendizaje Supervisado y Riesgo de Retraso
* **Simulador de Pedidos:**
  - Sliders interactivos de variables operativas: Distancia (km), Volumen ($m^3$), Prioridad (Alta/Normal/Baja), Ventana horaria (min), Cadena de frío (Sí/No), Hora pico (Sí/No), Nivel de tráfico (Bajo/Medio/Alto).
  - Predicción en tiempo real: Probabilidad y etiqueta binaria de riesgo de retraso calculada por el modelo serializado en `artifacts/`.
* **Comparador de Modelos:**
  - Visualización interactiva de métricas (Accuracy, F1-Score, Matriz de Confusión) comparando `LogisticRegression` vs `RandomForest`.

### Vista Semana 3: Clasificación Simbólica de Requerimientos
* **Analizador de Texto Libre:**
  - Campo de texto donde el usuario escribe o selecciona casos de prueba logísticos.
  - Desglose visual del árbol de reglas: palabras clave detectadas, reglas activadas y asignación justificada del área de IA según la taxonomía oficial.

### Vista Semana 5: Sistema Híbrido Trazable
* **Consulta Operativa en Lenguaje Natural:**
  - Campo de texto con las tres consultas de la guía como presets seleccionables.
  - La entrada se normaliza (minúsculas, sin tildes) antes de alimentar las tres técnicas.
* **Panel de Categoría Operativa:**
  - Clase predicha por `LogisticRegression` con barras de probabilidad por categoría (`predict_proba`).
* **Trazabilidad de la Decisión en Tres Nodos:**
  - **Reglas expertas:** acción disparada junto con la palabra exacta de la consulta que la activó (las reglas son datos estructurados `Regla(accion, palabras, descripcion)`, no lambdas anónimas).
  - **Evidencia documental:** protocolo SOP recuperado con medidor de similitud coseno TF-IDF.
  - **Clasificación supervisada:** categoría operativa y descripción del entrenamiento.
* **Catálogo de Ingeniería del Conocimiento:**
  - Visualización de las 5 reglas expertas del dominio logístico con sus palabras clave y acción operativa, alimentado por `/api/hibrido/contexto`.

### Vistas Futuras (Semanas 6 a 18 — Escalabilidad)
* **Semanas 7–12 (Corte 2):** Motor de restricciones operativas (capacidad de carga, ventanas de tiempo duras) y visualizador de ontología del dominio.
* **Semanas 13–18 (Corte 3):** Visor de Visión por Computador (inspección visual de paquetes con Canvas) y consola del ciclo de agentes (percibir $\rightarrow$ planificar $\rightarrow$ actuar $\rightarrow$ replanificar).

---

## 4. Estructura de Archivos Implementada

```text
ia-proyecto/
├── Dockerfile                  # Multi-stage build (Node/Corepack/pnpm + FastAPI)
├── docker-compose.yml          # Orquestación reproducible en un solo servicio
├── requirements.txt            # Se añaden dependencias web mínimas: fastapi, uvicorn
│
├── api/                        # Capa backend ligera
│   ├── __init__.py
│   ├── main.py                 # Instancia FastAPI, CORS y montaje estático
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── busqueda.py         # Endpoints de trazas paso a paso de A* y replanificación
│   │   ├── modelado.py         # Inferencia de riesgo de retraso
│   │   ├── clasificacion.py    # Evaluación de requerimientos simbólicos
│   │   ├── hibrido.py          # Respuesta trazable del sistema híbrido (Semana 5)
│   │   └── contenido.py        # Catálogo seguro de código e informes
│   ├── schemas/
│   │   ├── busqueda_dto.py     # Contratos Pydantic de búsqueda
│   │   ├── modelado_dto.py     # Contratos de inferencia supervisada
│   │   ├── clasificacion_dto.py
│   │   └── hibrido_dto.py      # Contrato de consulta del sistema híbrido
│   └── services/
│       ├── busqueda.py         # Proyección de trazas del core
│       ├── modelado.py         # Carga e inferencia del modelo
│       ├── clasificacion.py    # Adaptador del motor simbólico
│       ├── hibrido.py          # Adaptador del sistema híbrido (Semana 5)
│       └── contenido.py        # Allowlist, AST y lectura de Markdown
│
└── dashboard/                  # Frontend moderno en React
    ├── package.json
    ├── pnpm-lock.yaml          # Dependencias exactas; no se usa npm
    ├── vite.config.js
    ├── index.html
    └── src/
        ├── App.jsx             # Shell principal con selector de semanas
        ├── main.jsx
        ├── index.css
        ├── components/
        │   ├── Navbar.jsx
        │   ├── CodeExplainer.jsx    # Panel con resaltado de sintaxis y línea activa
        │   ├── CodeExplorer.jsx     # Código real y explicación línea a línea
        │   ├── MarkdownViewer.jsx   # Informes GFM, matemáticas, TOC y búsqueda
        │   ├── LearningHeader.jsx   # Cabecera común de vistas didácticas
        │   ├── WeekWorkspace.jsx    # Laboratorio / Código / Informe por semana
        │   ├── StepPlayer.jsx       # Barra de controles de reproducción
        │   ├── MetricsCard.jsx      # Tarjetas y tablas de métricas en vivo
        │   ├── GridCanvas.jsx       # SVG accesible para cuadrícula y grafo real
        │   └── learning.test.jsx    # Pruebas de código y Markdown
        ├── views/
        │   ├── Semana02View.jsx     # Vista interactiva de ML Supervisado
        │   ├── Semana03View.jsx     # Vista interactiva de Clasificador Simbólico
        │   ├── Semana04View.jsx     # Vista del Simulador A*, Heurísticas y Replanificación
        │   └── Semana05View.jsx     # Vista del Sistema Híbrido Trazable
        └── services/
            └── api.js               # Cliente HTTP fetch hacia la API
```

---

## 5. Plan de Ejecución por Fases

### Fase 1: Entorno, Contenedores y Configuración Base
- [x] Agregar dependencias de API a `requirements.txt` (`fastapi`, `uvicorn`, `pydantic`).
- [x] Crear estructura base de `api/` con FastAPI y habilitar CORS para desarrollo.
- [x] Inicializar proyecto `dashboard/` con Vite, React y Tailwind CSS.
- [x] Crear `Dockerfile` multi-stage y `docker-compose.yml` para una imagen reproducible que sirva API y SPA. El hot-reload queda disponible mediante la ejecución nativa de Vite/Uvicorn, evitando dos topologías Docker distintas.

### Fase 2: Backend de Trazabilidad Algorítmica (`api/services/busqueda.py`)
- [x] Implementar una proyección de trazas en la capa de servicios, validando que el resultado final coincida con los algoritmos de `src/busqueda/` y sin alterar sus contratos públicos:
  - Estado del nodo actual expandido.
  - Vecinos evaluados y cálculo de $g, h, f$.
  - Estado de la cola `open_set` y conjunto `closed_set`.
  - Línea de código ejecutada asociada al paso.
- [x] Exponer endpoint `/api/busqueda/a-estrella/simular` recibiendo: tipo de grafo (grid o Amazon), origen, destino, obstáculos bloqueados, algoritmo y heurística.
- [x] Exponer endpoint `/api/busqueda/replanificar` para simular evento de corte vial sobre la marcha.
- [x] Limitar cada snapshot a datos didácticos relevantes para evitar respuestas cuadráticas en los grafos completos de Amazon.

### Fase 3: Frontend del Simulador $A^*$ (Semana 4)
- [x] Construir componente `GridCanvas.jsx`: renderizado SVG de cuadrícula 5x5 y grafo Amazon, celdas de inicio/meta, muros interactivos y estados dinámicos.
- [x] Construir componente `CodeExplainer.jsx`: renderizado del código Python de $A^*$ con marcado dinámico de la línea en ejecución según el paso actual.
- [x] Construir `StepPlayer.jsx` con temporizador reactivo para reproducción automática configurable.
- [x] Conectar métricas en tiempo real en `Semana04View.jsx`.
- [x] Incluir navegación por teclado, estados de carga/error y preferencias de movimiento reducido.

### Fase 4: Frontend de Semanas 2 y 3
- [x] Conectar endpoints de inferencia de `src/modelado/riesgo_retraso.py` con sliders en `Semana02View.jsx`.
- [x] Conectar clasificador de `src/clasificacion/requerimientos.py` con `Semana03View.jsx`.
- [x] Si el modelo serializado no existe en un clon limpio, reconstruirlo de forma determinista desde `data/pedidos.csv` antes de inferir.

### Fase 5: Validación, Empaquetado y Documentación
- [x] Validar que `python -m unittest discover -s tests -v` continúe corriendo de forma completamente limpia en consola local sin Docker.
- [x] Validar que `docker compose up --build` levante backend y frontend y alcance estado `healthy`.
- [x] Actualizar [`README.md`](README.md) y [`PLAN-PROYECTO.md`](PLAN-PROYECTO.md) con la sección de uso del dashboard.

### Fase 6: Workspace de Aprendizaje y Gestión con pnpm
- [x] Sustituir npm por `pnpm@11.25.0`, `pnpm-lock.yaml`, Corepack y builds con `--frozen-lockfile`.
- [x] Ordenar la navegación lateral de forma numérica ascendente y abrir el recorrido en Semana 2.
- [x] Crear un catálogo backend con allowlist para todos los ejercicios e informes de Semanas 2–4.
- [x] Mostrar el código Python real con mapa AST, selección de líneas, reproducción y explicación línea a línea.
- [x] Sincronizar la traza del laboratorio de Semana 4 con líneas originales de A*, Dijkstra y BFS.
- [x] Renderizar cada informe Markdown con GFM, fórmulas KaTeX, tabla de contenido, búsqueda y vista de fuente.
- [x] Cargar bajo demanda el explorador y el visualizador para conservar un bundle inicial liviano.
- [x] Validar 55 pruebas Python, 2 pruebas frontend y el build de producción con pnpm.

### Fase 7: Semana 5 — Sistema Híbrido Trazable
- [x] Implementar `src/hibrido/sistema.py` con reglas expertas declarativas (datos, no lambdas), recuperación TF-IDF + coseno y clasificación con `predict_proba`.
- [x] Crear `data/base_conocimiento.txt` con 10 protocolos SOP y script reproducible `python -m src.sistema_hibrido`.
- [x] Exponer `/api/hibrido/responder` y `/api/hibrido/contexto` con contratos Pydantic.
- [x] Construir `Semana05View.jsx` con presets de la guía, barras de probabilidad, trazabilidad en tres nodos y catálogo de reglas.
- [x] Registrar la Semana 5 en el catálogo de contenido y crear `reports/sem-05-sistema-hibrido.md`.
- [x] Validar 67 pruebas Python y el build de producción con pnpm.

---

## 6. Criterios de Éxito y Calidad

1. **Fluidez:** Transiciones sin bloqueo perceptible, carga diferida de vistas pesadas y respeto a movimiento reducido.
2. **Fidelidad Académica:** Los resultados mostrados en el dashboard (costos, nodos expandidos, heurísticas) deben ser matemáticamente idénticos a los reportados en los informes técnicos ([`reports/sem-04-busqueda-rutas.md`](reports/sem-04-busqueda-rutas.md)).
3. **No Invasividad:** Cero modificaciones que alteren la API pública o los contratos de las clases en `src/`.
4. **Portabilidad Total:** Ejecución garantizada tanto vía Docker como de forma nativa en macOS, Linux y Windows.
5. **Accesibilidad y Resiliencia:** Controles operables con teclado, contraste legible, foco visible, respeto a `prefers-reduced-motion` y mensajes claros ante errores de red o entradas sin solución.
6. **Contrato Verificable:** DTO validados en la API, allowlist sin rutas arbitrarias, pruebas de servicios y componentes, y compilación de producción del frontend en cada validación.
