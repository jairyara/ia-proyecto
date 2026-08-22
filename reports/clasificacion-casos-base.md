# Clasificación de requerimientos por área de IA

Reporte generado por `python -m src.clasificador_requerimientos`.

## Configuración

- Entrada: `casos_ia.csv`
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

## Reglas propias del dominio

| Área | Vocabulario logístico agregado |
|---|---|
| Búsqueda y optimización | `flota`, `entrega`, `entregas`, `despacho`, `despachos`, `logistica`, `reparto`, `repartos`, `mensajeria`, `ultima milla` |
| Aprendizaje automático predictivo | `retraso`, `retrasos`, `pronostico`, `pronosticar`, `riesgo de retraso`, `tiempo de entrega`, `tiempos de entrega`, `volumen de envios`, `demanda de envios` |
| Sistemas expertos | `restriccion`, `restricciones`, `ventana horaria`, `ventanas horarias`, `capacidad del vehiculo`, `capacidad de los vehiculos`, `prioridad`, `cadena de frio`, `politica operativa` |
| Visión por computador | `paquete`, `paquetes`, `etiqueta`, `etiquetas`, `dano visible`, `verificacion visual`, `codigo de barras` |
| Sistemas de recomendación | `recomendacion`, `recomendaciones`, `alternativa de ruta`, `alternativas de ruta`, `preferencia del operador` |
| Procesamiento de lenguaje natural | `seguimiento`, `estado del envio`, `reclamos` |
| Robótica y sistemas autónomos | `dron de reparto`, `reparto autonomo`, `repartidor autonomo` |

## Clasificación de requerimientos

| ID | Requerimiento | Principal | Áreas detectadas | Evidencia principal | Esperada | Estado |
|---|---|---|---|---|---|---|
| CASO-001 | Detectar matrículas de vehículos a partir de imágenes capturadas por cámaras de seguridad. | Visión por computador | Visión por computador | `imagenes`, `camaras` | Visión por computador | Coincide |
| CASO-002 | Analizar comentarios de clientes para identificar si expresan opiniones positivas, negativas o neutrales. | Procesamiento de lenguaje natural | Procesamiento de lenguaje natural | `comentarios` | Procesamiento de lenguaje natural | Coincide |
| CASO-003 | Predecir qué clientes tienen mayor probabilidad de abandonar un servicio de telefonía móvil. | Aprendizaje automático predictivo | Aprendizaje automático predictivo | `predecir`, `probabilidad` | Aprendizaje automático predictivo | Coincide |
| CASO-004 | Determinar la ruta de entrega más corta para una flota de vehículos de una empresa de logística. | Búsqueda y optimización | Búsqueda y optimización | `ruta`, `flota`, `entrega`, `logistica` | Búsqueda y optimización | Coincide |
| CASO-005 | Recomendar películas a un usuario utilizando su historial de visualización y sus preferencias. | Sistemas de recomendación | Sistemas de recomendación | `recomendar`, `preferencias`, `historial de visualizacion` | Sistemas de recomendación | Coincide |
| CASO-006 | Detectar posibles fraudes analizando automáticamente transacciones bancarias. | Aprendizaje automático predictivo | Aprendizaje automático predictivo | `fraudes` | Aprendizaje automático predictivo | Coincide |
| CASO-007 | Identificar enfermedades de plantas mediante fotografías de sus hojas. | Visión por computador | Visión por computador | `fotografias` | Visión por computador | Coincide |
| CASO-008 | Crear un chatbot capaz de responder preguntas frecuentes de los estudiantes de una universidad. | Procesamiento de lenguaje natural | Procesamiento de lenguaje natural | `chatbot` | Procesamiento de lenguaje natural | Coincide |
| CASO-009 | Predecir la demanda mensual de energía eléctrica utilizando registros históricos de consumo. | Aprendizaje automático predictivo | Aprendizaje automático predictivo | `predecir`, `demanda` | Aprendizaje automático predictivo | Coincide |
| CASO-010 | Construir un sistema que sugiera posibles diagnósticos médicos a partir de síntomas ingresados por un profesional. | Sistemas expertos | Sistemas expertos | `diagnosticos` | Sistemas expertos | Coincide |
| CASO-011 | Reconocer rostros para permitir el ingreso autorizado a un laboratorio. | Visión por computador | Visión por computador | `rostros` | Visión por computador | Coincide |
| CASO-012 | Clasificar automáticamente correos electrónicos como spam o correo legítimo según su contenido. | Procesamiento de lenguaje natural | Procesamiento de lenguaje natural | `correo`, `correos` | Procesamiento de lenguaje natural | Coincide |
| CASO-013 | Programar un robot móvil para desplazarse dentro de una bodega evitando obstáculos. | Robótica y sistemas autónomos | Robótica y sistemas autónomos | `robot`, `obstaculos` | Robótica y sistemas autónomos | Coincide |
| CASO-014 | Asignar automáticamente horarios de clase evitando conflictos entre profesores, salones y grupos. | Búsqueda y optimización | Búsqueda y optimización | `horarios` | Búsqueda y optimización | Coincide |
| CASO-015 | Detectar fallas futuras en maquinaria industrial utilizando información histórica de sensores. | Aprendizaje automático predictivo | Aprendizaje automático predictivo | `sensores` | Aprendizaje automático predictivo | Coincide |
| CASO-016 | Extraer nombres, fechas y organizaciones mencionadas dentro de contratos escritos. | Procesamiento de lenguaje natural | Procesamiento de lenguaje natural | `contratos`, `nombres` | Procesamiento de lenguaje natural | Coincide |
| CASO-017 | Identificar peatones y señales de tránsito en las imágenes capturadas por un vehículo autónomo. | Visión por computador | Visión por computador, Robótica y sistemas autónomos | `imagenes`, `peatones`, `senales` | Visión por computador | Coincide |
| CASO-018 | Construir un sistema basado en reglas que determine si una solicitud de crédito cumple las políticas de una organización. | Sistemas expertos | Sistemas expertos | `reglas`, `politicas`, `solicitud de credito` | Sistemas expertos | Coincide |
| CASO-019 | Diseñar un dron capaz de ajustar automáticamente su trayectoria para llegar a un destino. | Robótica y sistemas autónomos | Robótica y sistemas autónomos | `dron`, `trayectoria` | Robótica y sistemas autónomos | Coincide |
| CASO-020 | Seleccionar la combinación óptima de productos que puede transportar un vehículo respetando su capacidad máxima. | Búsqueda y optimización | Búsqueda y optimización | `combinacion optima`, `capacidad maxima` | Búsqueda y optimización | Coincide |

## Resultado frente a la referencia

Coincidencia: **100.00%** (20/20).

## Limitaciones

- Las reglas dependen del vocabulario explícito y no comprenden el contexto.
- Los empates se resuelven por el orden de las categorías, por lo que deben revisarse.
- Una coincidencia con la referencia valida los casos actuales, no generaliza a todo el dominio.
- La salida conserva áreas secundarias para no reducir requerimientos híbridos a una sola técnica.
