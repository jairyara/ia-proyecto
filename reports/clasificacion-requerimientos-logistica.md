# Clasificación de requerimientos por área de IA

Reporte generado por `python -m src.clasificador_requerimientos`.

## Configuración

- Entrada: `requerimientos_logistica.csv`
- Casos procesados: **20**
- Método: reglas deterministas sobre palabras y frases completas.
- Desempate: orden documentado de las áreas en el código.

## Componentes y áreas

| Área | Componente del proyecto |
|---|---|
| Visión por computador | Verificación de paquetes a partir de imágenes. |
| Procesamiento de lenguaje natural | Explicaciones o novedades expresadas en lenguaje natural. |
| Aprendizaje automático predictivo | Estimación de demanda o clasificación del riesgo de retraso. |
| Sistemas de recomendación | Presentación de planes y alternativas al operador. |
| Búsqueda y optimización | Planificación de rutas con A* sobre el grafo de entregas. |
| Sistemas expertos | Validación trazable de restricciones operativas. |
| Robótica y sistemas autónomos | Ciclo de control y replanificación ante novedades. |

## Cinco reglas propias del dominio

| Área | Vocabulario logístico agregado |
|---|---|
| Búsqueda y optimización | `flota`, `entrega`, `entregas`, `despacho`, `despachos`, `logistica` |
| Aprendizaje automático predictivo | `retraso`, `retrasos`, `pronostico`, `pronosticar`, `riesgo de retraso`, `tiempo de entrega` |
| Sistemas expertos | `restriccion`, `restricciones`, `ventana horaria`, `ventanas horarias`, `capacidad del vehiculo`, `capacidad de los vehiculos`, `prioridad`, `cadena de frio`, `politica operativa` |
| Visión por computador | `paquete`, `paquetes`, `etiqueta`, `etiquetas`, `dano visible`, `verificacion visual` |
| Sistemas de recomendación | `recomendacion`, `recomendaciones`, `alternativa de ruta`, `alternativas de ruta`, `preferencia del operador` |

## Clasificación de requerimientos

| ID | Requerimiento | Principal | Áreas detectadas | Evidencia principal | Esperada | Estado |
|---|---|---|---|---|---|---|
| REQ-001 | Calcular la ruta de menor distancia sobre el grafo de entregas con A*. | Búsqueda y optimización | Búsqueda y optimización | `a estrella`, `ruta`, `grafo`, `distancia`, `entregas` | Búsqueda y optimización | Coincide |
| REQ-002 | Optimizar los despachos y las rutas disponibles para toda la flota. | Búsqueda y optimización | Búsqueda y optimización | `rutas`, `optimizar`, `flota`, `despachos` | Búsqueda y optimización | Coincide |
| REQ-003 | Predecir el riesgo de retraso y el tiempo de entrega con aprendizaje supervisado. | Aprendizaje automático predictivo | Aprendizaje automático predictivo, Búsqueda y optimización | `predecir`, `aprendizaje supervisado`, `retraso`, `riesgo de retraso`, `tiempo de entrega` | Aprendizaje automático predictivo | Coincide |
| REQ-004 | Pronosticar la demanda diaria con un modelo predictivo antes de asignar vehículos. | Aprendizaje automático predictivo | Aprendizaje automático predictivo | `demanda`, `modelo predictivo`, `pronosticar` | Aprendizaje automático predictivo | Coincide |
| REQ-005 | Validar las restricciones de capacidad del vehículo y ventana horaria. | Sistemas expertos | Sistemas expertos | `restricciones`, `ventana horaria`, `capacidad del vehiculo` | Sistemas expertos | Coincide |
| REQ-006 | Aplicar reglas de prioridad y cadena de frío antes de aprobar el plan. | Sistemas expertos | Sistemas expertos | `reglas`, `prioridad`, `cadena de frio` | Sistemas expertos | Coincide |
| REQ-007 | Inspeccionar una imagen del paquete para detectar daño visible. | Visión por computador | Visión por computador | `imagen`, `paquete`, `dano visible` | Visión por computador | Coincide |
| REQ-008 | Usar una cámara para la verificación visual de etiquetas en los paquetes. | Visión por computador | Visión por computador | `camara`, `paquetes`, `etiquetas`, `verificacion visual` | Visión por computador | Coincide |
| REQ-009 | Un agente autónomo debe percibir una vía cerrada y replanificar durante el ciclo de control. | Robótica y sistemas autónomos | Robótica y sistemas autónomos | `agente autonomo`, `ciclo de control`, `percibir`, `replanificar` | Robótica y sistemas autónomos | Coincide |
| REQ-010 | Recomendar alternativas de ruta según la preferencia del operador. | Sistemas de recomendación | Sistemas de recomendación, Búsqueda y optimización | `recomendar`, `alternativas de ruta`, `preferencia del operador` | Sistemas de recomendación | Coincide |
| REQ-011 | Generar una explicación textual en lenguaje natural para el operador. | Procesamiento de lenguaje natural | Procesamiento de lenguaje natural | `lenguaje` | Procesamiento de lenguaje natural | Coincide |
| REQ-012 | Calcular una ruta A* y validar sus ventanas horarias con reglas auditables. | Búsqueda y optimización | Búsqueda y optimización, Sistemas expertos | `a estrella`, `ruta` | Búsqueda y optimización | Coincide |
| REQ-013 | Predecir retrasos de los pedidos mediante un pronóstico operativo. | Aprendizaje automático predictivo | Aprendizaje automático predictivo | `predecir`, `retrasos`, `pronostico` | Aprendizaje automático predictivo | Coincide |
| REQ-014 | Validar una política operativa de cadena de frío antes del despacho. | Sistemas expertos | Sistemas expertos, Búsqueda y optimización | `politica`, `cadena de frio`, `politica operativa` | Sistemas expertos | Coincide |
| REQ-015 | Reconocer la etiqueta de un paquete a partir de una fotografía. | Visión por computador | Visión por computador | `fotografia`, `paquete`, `etiqueta` | Visión por computador | Coincide |
| REQ-016 | Encontrar el camino de menor distancia entre la bodega y una entrega. | Búsqueda y optimización | Búsqueda y optimización | `camino`, `distancia`, `entrega` | Búsqueda y optimización | Coincide |
| REQ-017 | Replanificar cuando aparece un pedido nuevo durante el ciclo de control. | Robótica y sistemas autónomos | Robótica y sistemas autónomos | `ciclo de control`, `replanificar` | Robótica y sistemas autónomos | Coincide |
| REQ-018 | Presentar recomendaciones y alternativas de ruta al operador. | Sistemas de recomendación | Sistemas de recomendación, Búsqueda y optimización | `recomendaciones`, `alternativas de ruta` | Sistemas de recomendación | Coincide |
| REQ-019 | Interpretar mensajes de texto con novedades de la jornada. | Procesamiento de lenguaje natural | Procesamiento de lenguaje natural | `texto` | Procesamiento de lenguaje natural | Coincide |
| REQ-020 | Comparar rutas de la flota y restricciones de capacidad de los vehículos. | Búsqueda y optimización | Búsqueda y optimización, Sistemas expertos | `rutas`, `flota` | Búsqueda y optimización | Coincide |

## Resultado frente a la referencia

Coincidencia: **100.00%** (20/20).

## Limitaciones

- Las reglas dependen del vocabulario explícito y no comprenden el contexto.
- Los empates se resuelven por el orden de las categorías, por lo que deben revisarse.
- Una coincidencia con la referencia valida los casos actuales, no generaliza a todo el dominio.
- La salida conserva áreas secundarias para no reducir requerimientos híbridos a una sola técnica.
