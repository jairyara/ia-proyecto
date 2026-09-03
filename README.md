# Sistema inteligente para logística

Proyecto 8 del curso **Inteligencia Artificial** de décimo semestre. El
sistema busca apoyar la planificación de rutas de reparto mediante una
arquitectura híbrida que combina búsqueda heurística, aprendizaje automático
y conocimiento explícito del dominio logístico.

## Problema y justificación

Una operación de distribución debe decidir recorridos eficientes sin ignorar
la capacidad de los vehículos, las ventanas horarias, la prioridad de los
clientes ni requisitos como la cadena de frío. Además, la demanda, los retrasos
y eventos como el cierre de una vía introducen incertidumbre durante la
jornada.

El proyecto aborda el problema como un sistema de IA completo y trazable:

1. representa la zona de entrega mediante un grafo;
2. obtiene rutas con A* y las compara con búsqueda no informada;
3. estima demanda o riesgo de retraso con aprendizaje supervisado;
4. valida los planes con reglas operativas explícitas; y
5. replantea la solución cuando cambia el entorno.

Este enfoque permite evaluar por separado la calidad de las rutas, las métricas
predictivas y las reglas activadas, en lugar de tratar la solución como una
caja negra. Su valor práctico consiste en reducir costos y tiempos de entrega,
garantizar de manera auditable las restricciones operativas y responder a
imprevistos mediante replanificación automática.

La descripción completa se encuentra en la
[`justificación oficial del proyecto`](docs/justificacion-proyecto-08.pdf).

## Objetivos

### Objetivo general

Construir un sistema inteligente híbrido que planifique y ajuste rutas de
distribución de forma eficiente, verificable y compatible con las restricciones
de la operación.

### Objetivos específicos

- Modelar puntos de entrega y vías como un grafo con costos de distancia y
  tiempo.
- Implementar A* y compararlo con una estrategia de búsqueda no informada.
- Entrenar y validar un modelo predictivo que anticipe la operación.
- Representar restricciones logísticas mediante reglas con trazabilidad.
- Integrar percepción de novedades y replanificación en un ciclo con condición
  de parada.
- Documentar resultados, supuestos, limitaciones y métricas en cada corte.

## Casos de uso

1. **Última milla y domicilios urbanos:** minimizar distancia y tiempo total de
   las rutas diarias.

## Taxonomía de IA aplicada

| Área | Papel en el sistema | Validación prevista |
|---|---|---|
| Búsqueda y optimización | Núcleo de planificación: A* sobre el grafo de entregas | Costo de ruta y nodos expandidos frente a búsqueda no informada |
| Aprendizaje automático predictivo | Demanda o riesgo de retraso | Accuracy, F1 y matriz de confusión según la tarea elegida |
| Sistemas expertos | Capacidad, ventanas horarias, prioridades y cadena de frío | Reglas activadas y decisión explicada por plan |
| Visión por computador | Verificación visual de paquetes | Métrica acorde con la tarea visual que se defina |
| Robótica y sistemas autónomos | Ciclo percibir–planificar–actuar y replanificación | Cumplimiento de la condición de parada y respuesta a eventos |
| Sistemas de recomendación | Presentación de planes y alternativas al operador | Calidad y factibilidad de las alternativas |
| Procesamiento de lenguaje natural | Área complementaria para explicaciones o captura de novedades | Alcance sujeto a las necesidades confirmadas del curso |

La línea base actual incluye un clasificador simbólico
(`src/clasificador_requerimientos.py`), un generador sintético reproducible de
pedidos (`src/generador_pedidos.py`) y un baseline supervisado de riesgo de
retraso (`src/modelo_riesgo.py`).

- El clasificador usa vocabulario propio del dominio logístico (rutas y última
  milla, demanda y riesgo de retraso, restricciones operativas, verificación de
  paquetes, seguimiento de envíos y reparto autónomo) y reporta evidencia de
  reglas activadas.
- El generador crea `data/pedidos.csv` con seed fija y distribuciones
  documentadas; la etiqueta de retraso sigue una regla logística con ruido
  controlado.
- El baseline supervisado compara LogisticRegression y RandomForest, elige por
  F1 y guarda métricas y el modelo en `artifacts/`.

## Dashboard interactivo

El repositorio incluye **Órbita**, un laboratorio web para sustentar los tres
componentes ya implementados sin reemplazar su ejecución académica:

- reproduce paso a paso A*, Dijkstra y BFS sobre una cuadrícula o rutas reales
  de Amazon Last Mile, mostrando frontera, cerrados, costos y línea activa;
- permite bloquear un tramo y observar la replanificación;
- predice riesgo de retraso con el pipeline supervisado y muestra aportes locales;
- clasifica texto logístico con la evidencia exacta de las reglas simbólicas.

FastAPI actúa como adaptador de `src/`; el resultado canónico de cada algoritmo
sigue proviniendo de los módulos Python. Si el modelo ignorado en `artifacts/`
no existe en un clon limpio, la API lo reconstruye de forma determinista desde
`data/pedidos.csv`.

## Estado y alcance

El sistema cuenta hoy con una base verificable:

- estructura reproducible y convenciones de trabajo;
- taxonomía del dominio logístico;
- clasificador simbólico de requerimientos;
- 20 requerimientos del dominio con referencia manual;
- baseline supervisado de riesgo de retraso (accuracy, F1, matriz de confusión);
- búsqueda heurística A* con líneas base y replanificación dinámica;
- sistema híbrido trazable (reglas expertas + TF-IDF + clasificación) con
  base de conocimiento de 10 protocolos operativos;
- validación automática y reportes reproducibles.

Los siguientes módulos se incorporan según el roadmap, los cortes y las
decisiones abiertas de [`PLAN-PROYECTO.md`](PLAN-PROYECTO.md).

## Estructura

```text
.
├── artifacts/          # Modelos y artefactos serializados
├── api/                # API FastAPI y servicios de trazabilidad/inferencia
├── data/               # Datos versionados (sintéticos y Amazon Last Mile)
├── dashboard/          # SPA React + Vite + Tailwind del laboratorio Órbita
├── docs/               # Fuentes y justificaciones oficiales del curso
├── notebooks/          # Exploración y análisis reproducible
├── reports/            # Evidencia, reportes y métricas por tema
├── src/                # Código fuente modular
│   ├── comun/          # Utilidades comunes (cálculo geodésico Haversine, cliente HTTP)
│   ├── datos/          # Ingesta, extracción (Amazon Last Mile) y generación sintética
│   ├── modelado/       # Modelos predictivos supervisados y evaluación de métricas
│   ├── clasificacion/  # Clasificador simbólico y reglas de taxonomía
│   ├── busqueda/       # Búsqueda heurística A*, líneas base no informadas y replanificación
│   └── hibrido/        # Sistema híbrido: reglas expertas + TF-IDF/coseno + clasificación
└── tests/              # Pruebas automatizadas unitarias y de integración
```

## Configuración

La guía del curso requiere **Python 3.13.x**.

```bash
python3.13 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Para ejecutar el frontend sin Docker se requiere **Node.js 22.13 o superior**;
Corepack selecciona automáticamente la versión fijada `pnpm@11.25.0` desde
`dashboard/package.json`.

## Uso

Los módulos pueden ejecutarse a través de sus paquetes o mediante los accesos directos en `src/`:

1. **Clasificación simbólica de requerimientos:**
   ```bash
   python -m src.clasificacion.requerimientos --fail-on-mismatch
   # o: python -m src.clasificador_requerimientos --fail-on-mismatch
   ```

2. **Pipeline predictivo supervisado (datos sintéticos):**
   ```bash
   python -m src.datos.sintetico
   python -m src.modelado.riesgo_retraso
   # o: python -m src.generador_pedidos && python -m src.modelo_riesgo
   ```

3. **Curaduría y extracción de Amazon Last Mile (ALMRRC 2021):**
   ```bash
   python -m src.datos.amazon
   # o: python -m src.extraer_datos_amazon
   ```

4. **Búsqueda heurística A*, comparación con Dijkstra y replanificación:**
   ```bash
   python -m src.busqueda_rutas
   ```

5. **Sistema híbrido trazable (reglas + TF-IDF + clasificación):**
   ```bash
   python -m src.sistema_hibrido
   ```

6. **Pruebas automatizadas:**
   ```bash
   python -m unittest discover -s tests -v
   ```

7. **Dashboard web, ejecución local con recarga automática:**
   ```bash
   # Terminal 1, desde la raíz y con .venv activo
   uvicorn api.main:app --reload --port 8000

   # Terminal 2
   cd dashboard
   corepack enable
   pnpm install --frozen-lockfile
   pnpm dev
   ```
   Abre `http://localhost:5173`. Vite redirige `/api` a FastAPI.
   El dashboard recorre las semanas en orden ascendente y cada una ofrece las
   vistas **Laboratorio**, **Código explicado** e **Informe**. La segunda lee
   los módulos Python reales, explica cada línea y permite abrir la línea
   seleccionada directamente en **PyCharm** o **VS Code**; la tercera renderiza
   los reportes Markdown con tabla de contenido, búsqueda, tablas y fórmulas.

   El navegador solicitará autorización para abrir el IDE la primera vez. Con
   Docker, Compose transmite automáticamente la ruta actual del repositorio al
   contenedor. Si se ejecuta desde otro directorio, se puede indicar de forma
   explícita:

   ```bash
   DASHBOARD_EDITOR_WORKSPACE=/ruta/absoluta/ia-proyecto docker compose up --build
   ```

7. **Dashboard completo con Docker:**
   ```bash
   docker compose up --build
   ```
   Abre `http://localhost:8000`. La imagen multi-stage compila la SPA y FastAPI
   la sirve junto con los endpoints. La documentación OpenAPI queda en
   `http://localhost:8000/docs`.

Para una comprobación de producción del frontend sin Docker:

```bash
cd dashboard
corepack enable
pnpm install --frozen-lockfile
pnpm test
pnpm build
```

## Documentación relacionada

- [`PLAN-PROYECTO.md`](PLAN-PROYECTO.md) — roadmap, cortes y decisiones
  abiertas.
- [`CONTRIBUTING.md`](CONTRIBUTING.md) — commits, calidad y reportes.
- [`CHANGELOG.md`](CHANGELOG.md) — historial acumulativo del proyecto.
- [`docs/justificacion-proyecto-08.pdf`](docs/justificacion-proyecto-08.pdf) —
  descripción, justificación, alineación y casos de uso oficiales.

## Equipo

- Jair Yara
- Catherinne Gutierrez
