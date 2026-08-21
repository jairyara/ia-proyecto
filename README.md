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
caja negra.

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

La línea base actual es un clasificador simbólico de requerimientos logísticos
disponible en `src/semana03_taxonomia.py`.

## Estado y alcance

El repositorio se encuentra **nivelado con los contenidos confirmados hasta la
semana 3**:

- estructura reproducible y convenciones de trabajo;
- taxonomía del dominio logístico;
- reglas simbólicas para clasificar requerimientos;
- conjunto inicial de casos, validación automática y reporte reproducible.

Las semanas posteriores se incorporan cuando se confirmen los materiales del
curso. El alcance de cada corte y las decisiones abiertas están en
[`PLAN-PROYECTO.md`](PLAN-PROYECTO.md).

## Estructura

```text
.
├── artifacts/   # Modelos y artefactos generados
├── data/        # Datos de entrada versionados
├── notebooks/   # Exploración reproducible
├── reports/     # Evidencia y resultados por semana
├── src/         # Código fuente
└── tests/       # Pruebas automatizadas
```

## Configuración

Se recomienda Python 3.11 o superior.

```bash
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt
```

## Uso

Ejecutar la línea base de taxonomía desde la raíz del repositorio:

```bash
python3 -m src.semana03_taxonomia
```

La ejecución lee `data/requerimientos_logistica.csv` y actualiza
`reports/semana03.md`. Para ver las opciones disponibles:

```bash
python3 -m src.semana03_taxonomia --help
```

Ejecutar las pruebas:

```bash
python3 -m unittest discover -s tests -v
```

## Documentación relacionada

- [`PLAN-PROYECTO.md`](PLAN-PROYECTO.md) — roadmap, cortes y decisiones
  abiertas.
- [`CONTRIBUTING.md`](CONTRIBUTING.md) — commits, calidad y reportes.
- [`CHANGELOG.md`](CHANGELOG.md) — historial acumulativo del proyecto.
- `../ia-semestre/TEMATICAS.md` — temáticas y prácticas del curso en el
  repositorio académico complementario.

## Equipo

- Jair Yara
- Catherinne Gutierrez
