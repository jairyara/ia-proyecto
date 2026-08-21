# Semana 03 — Taxonomía del dominio logístico

Reporte generado por `python3 -m src.semana03_taxonomia`.

## Configuración

- Entrada: `requerimientos_logistica.csv`
- Casos procesados: **12**
- Método: reglas deterministas sobre palabras y frases completas.
- Desempate: orden documentado de las áreas en el código.

## Componentes y áreas

| Área | Componente del proyecto |
|---|---|
| Búsqueda y optimización | Planificación de rutas con A* sobre el grafo de entregas. |
| Aprendizaje automático predictivo | Estimación de demanda o clasificación del riesgo de retraso. |
| Sistemas expertos | Validación trazable de restricciones operativas. |
| Visión por computador | Verificación de paquetes a partir de imágenes. |
| Robótica y sistemas autónomos | Ciclo de control y replanificación ante novedades. |
| Sistemas de recomendación | Presentación de planes y alternativas al operador. |
| Procesamiento de lenguaje natural | Explicaciones o novedades expresadas en lenguaje natural. |

## Clasificación de requerimientos

| ID | Requerimiento | Principal | Áreas detectadas | Evidencia principal | Esperada | Estado |
|---|---|---|---|---|---|---|
| REQ-001 | Calcular la ruta de menor distancia sobre el grafo de entregas con A*. | Búsqueda y optimización | Búsqueda y optimización | `a estrella`, `ruta`, `grafo`, `distancia`, `entregas` | Búsqueda y optimización | Coincide |
| REQ-002 | Optimizar los despachos y las rutas disponibles para toda la flota. | Búsqueda y optimización | Búsqueda y optimización | `rutas`, `optimizar`, `flota`, `despachos` | Búsqueda y optimización | Coincide |
| REQ-003 | Predecir el riesgo de retraso y el tiempo de entrega con aprendizaje supervisado. | Aprendizaje automático predictivo | Aprendizaje automático predictivo, Búsqueda y optimización | `predecir`, `aprendizaje supervisado`, `riesgo de retraso`, `retraso`, `tiempo de entrega` | Aprendizaje automático predictivo | Coincide |
| REQ-004 | Pronosticar la demanda diaria con un modelo predictivo antes de asignar vehículos. | Aprendizaje automático predictivo | Aprendizaje automático predictivo | `modelo predictivo`, `pronosticar`, `demanda` | Aprendizaje automático predictivo | Coincide |
| REQ-005 | Validar las restricciones de capacidad del vehículo y ventana horaria. | Sistemas expertos | Sistemas expertos | `restricciones`, `ventana horaria`, `capacidad del vehiculo` | Sistemas expertos | Coincide |
| REQ-006 | Aplicar reglas de prioridad y cadena de frío antes de aprobar el plan. | Sistemas expertos | Sistemas expertos | `reglas`, `prioridad`, `cadena de frio` | Sistemas expertos | Coincide |
| REQ-007 | Inspeccionar una imagen del paquete para detectar daño visible. | Visión por computador | Visión por computador | `imagen`, `paquete`, `dano visible` | Visión por computador | Coincide |
| REQ-008 | Usar una cámara para la verificación visual de etiquetas en los paquetes. | Visión por computador | Visión por computador | `camara`, `paquetes`, `etiquetas`, `verificacion visual` | Visión por computador | Coincide |
| REQ-009 | Un agente autónomo debe percibir una vía cerrada y replanificar durante el ciclo de control. | Robótica y sistemas autónomos | Robótica y sistemas autónomos | `agente autonomo`, `ciclo de control`, `percibir`, `replanificar`, `via cerrada` | Robótica y sistemas autónomos | Coincide |
| REQ-010 | Recomendar alternativas de ruta según la preferencia del operador. | Sistemas de recomendación | Sistemas de recomendación, Búsqueda y optimización | `recomendar`, `alternativas de ruta`, `preferencia del operador` | Sistemas de recomendación | Coincide |
| REQ-011 | Generar una explicación textual en lenguaje natural para el operador. | Procesamiento de lenguaje natural | Procesamiento de lenguaje natural | `lenguaje natural`, `explicacion textual` | Procesamiento de lenguaje natural | Coincide |
| REQ-012 | Calcular una ruta A* y validar sus ventanas horarias con reglas auditables. | Búsqueda y optimización | Búsqueda y optimización, Sistemas expertos | `a estrella`, `ruta` | Búsqueda y optimización | Coincide |

## Resultado frente a la referencia

Coincidencia: **100.00%** (12/12).

## Limitaciones

- Las reglas dependen del vocabulario explícito y no comprenden el contexto.
- Los empates se resuelven por el orden de las categorías, por lo que deben revisarse.
- Una coincidencia con la referencia valida los casos actuales, no generaliza a todo el dominio.
- La salida conserva áreas secundarias para no reducir requerimientos híbridos a una sola técnica.
