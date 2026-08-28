# Dataset Amazon Last Mile Routing Challenge (ALMRRC 2021)

Reporte generado automáticamente por `python -m src.extraer_datos_amazon`.

## Resumen general

- **Fuente:** AWS Open Data Registry (`s3://amazon-last-mile-challenges/almrrc2021/`).
- **Rutas muestreadas:** 100 rutas estratificadas.
- **Total de paradas/pedidos limpios:** 14,411 registros.
- **Total de paquetes individuales:** 23,557 paquetes.
- **Grafos completos para búsqueda A\*:** 13 rutas con matrices NxN de tiempos.
- **Destino CSV tabular:** `/Users/jyarar/projects/u/x-semestre/ia-proyecto/data/amazon_pedidos.csv`
- **Destino grafos de muestra:** `/Users/jyarar/projects/u/x-semestre/ia-proyecto/data/amazon_rutas_muestra.json`

## Distribución por estación de distribución (Centros logísticos)

| Estación | Paradas | Paquetes | Dist. Depósito Promedio (km) | Tasa Riesgo Retraso |
|---|---:|---:|---:|---:|
| `DAU1` | 861 | 1,271 | 19.88 km | 7.3% |
| `DBO1` | 720 | 1,298 | 10.07 km | 3.9% |
| `DBO2` | 878 | 1,687 | 9.54 km | 1.9% |
| `DBO3` | 1,410 | 2,089 | 16.68 km | 7.6% |
| `DCH1` | 814 | 1,269 | 8.93 km | 1.1% |
| `DCH2` | 551 | 1,182 | 9.72 km | 1.5% |
| `DCH3` | 920 | 1,259 | 14.30 km | 3.4% |
| `DCH4` | 817 | 1,241 | 23.49 km | 8.2% |
| `DLA3` | 643 | 1,113 | 15.63 km | 14.2% |
| `DLA4` | 650 | 1,143 | 15.63 km | 11.4% |
| `DLA5` | 841 | 1,224 | 16.23 km | 6.8% |
| `DLA7` | 1,277 | 1,978 | 19.08 km | 8.6% |
| `DLA8` | 689 | 1,163 | 11.74 km | 6.8% |
| `DLA9` | 986 | 1,652 | 13.39 km | 10.4% |
| `DSE2` | 610 | 1,320 | 9.03 km | 3.1% |
| `DSE4` | 799 | 1,327 | 22.49 km | 16.5% |
| `DSE5` | 945 | 1,341 | 20.27 km | 6.3% |

## Estadísticas descriptivas de variables logísticas

| Variable | Mínimo | Promedio | Mediana | Máximo | Desv. Estándar |
|---|---:|---:|---:|---:|---:|
| `distancia_deposito_km` | 0.00 | 15.50 | 14.90 | 39.48 | 8.00 |
| `num_paquetes` | 0 | 1.63 | 1 | 35 | 1.42 |
| `volumen_total_m3` | 0.0000 | 0.0186 | 0.0095 | 0.8774 | 0.0299 |
| `tiempo_servicio_seg` | 0.0 | 74.0 | 56.0 | 2644.0 | 75.5 |

## Diccionario de campos (`data/amazon_pedidos.csv`)

| Campo | Tipo | Descripción |
|---|---|---|
| `pedido_id` | String | Identificador correlativo del pedido/parada (`AMZ-XXXXX`). |
| `route_id` | String | UUID de la ruta de entrega oficial en Amazon. |
| `stop_id` | String | Código de parada alfanumérico dentro de la ruta (e.g. `AH`, `AK`). |
| `station_code` | String | Código de la estación logística de origen (e.g. `DLA7`, `DCH4`). |
| `fecha` | String | Fecha de la jornada en formato `AAAA-MM-DD`. |
| `hora_salida_utc` | String | Hora de salida del vehículo en formato UTC. |
| `tipo_parada` | String | Tipo de punto: `Station` (depósito central) o `Dropoff` (entrega). |
| `lat`, `lng` | Float | Coordenadas geográficas exactas de la parada. |
| `zone_id` | String | Microzona logística de asignación de ruta. |
| `distancia_deposito_km` | Float | Distancia geodésica Haversine desde el depósito de origen. |
| `num_paquetes` | Entero | Cantidad de paquetes a entregar en la parada. |
| `volumen_total_m3` | Float | Volumen cúbico total de los paquetes ($m^3$). |
| `volumen_promedio_m3` | Float | Volumen cúbico promedio por paquete ($m^3$). |
| `tiempo_servicio_seg` | Float | Tiempo de servicio programado en segundos por parada. |
| `tiene_ventana_horaria` | Entero (0/1) | Indicador binario si la entrega tiene ventana horaria comprometida. |
| `duracion_ventana_min` | Float | Duración de la ventana horaria en minutos (0 si no aplica). |
| `secuencia_real` | Entero | Posición de visita real ejecutada por el repartidor. |
| `capacidad_vehiculo_m3` | Float | Capacidad de carga del vehículo en metros cúbicos. |
| `retrasado_estimado` | Entero (0/1) | Etiqueta de riesgo de retraso derivada para aprendizaje supervisado. |

## Calidad y limpieza de datos

- **Valores nulos no controlados:** 0 (todas las zonas vacías se normalizan a `'SIN_ZONA'`, ventanas nulas a `0`).
- **Integridad referencial:** Cada parada está vinculada a su ruta, coordenadas y secuencia real.
- **Compatibilidad:** Directamente usable por `pandas` y `scikit-learn` sin transformaciones previas requeridas.
