# Semana 07 — Evidencia reproducible de representaciones

> Generado por `python -m src.representaciones_reconocimiento`.

## 1. Caso oficial de clase

- Muestra: `[72.0, 0.85, 3.0]`
- Referencia: `[70.0, 0.8, 2.0]`
- Distancia euclidiana: `2.237`
- Conclusión simbólica: `riesgo_termico`

| Secuencia | Estado final | ¿Aceptada? |
|---|---|---|
| `1101` | `q2` | **True** |
| `1110` | `q1` | **False** |
| `0001` | `q2` | **True** |

## 2. Datos reales Amazon

- Registros procesados: **14,411**.
- Rutas: **100**.
- Variables: `['distancia_deposito_km', 'volumen_total_m3', 'tiempo_servicio_seg']`.
- Mediana: `[14.9, 0.0095, 56.0]`.
- P75: `[20.4655, 0.0213, 85.0]`.
- IQR: `[11.099499999999999, 0.0177, 45.8]`.

### Distribución de hechos derivados

| Hechos activados | Registros |
|---:|---:|
| 0 | 6,099 |
| 1 | 6,094 |
| 2 | 2,025 |
| 3 | 193 |

## 3. Perfiles demostrativos reales

| Criterio | Pedido | Vector | Distancia normalizada | Hechos |
|---|---|---|---:|---|
| Más cercana a la mediana | `AMZ-06380` | `[15.086, 0.0092, 58.0]` | 0.050 | `[]` |
| Mayor distancia | `AMZ-05429` | `[39.483, 0.0045, 35.0]` | 2.279 | `['parada_lejana']` |
| Mayor volumen | `AMZ-05050` | `[32.377, 0.8774, 27.5]` | 49.063 | `['parada_lejana', 'volumen_alto']` |
| Mayor tiempo de servicio | `AMZ-06618` | `[18.094, 0.0028, 2644.0]` | 56.509 | `['servicio_prolongado']` |
| Supera los tres percentiles 75 | `AMZ-00150` | `[22.656, 0.0465, 116.8]` | 2.573 | `['parada_lejana', 'volumen_alto', 'servicio_prolongado']` |

## 4. AFD logístico POD — escenarios controlados

> Amazon no registra eventos A/V/F/C; estas secuencias son pruebas diseñadas.

| Secuencia | Estado final | ¿Aceptada? |
|---|---|---|
| `AVF` | `q3` | **True** |
| `AVC` | `q_fallo` | **False** |
| `AF` | `q_fallo` | **False** |
| `AV` | `q2` | **False** |

## 5. Procedencia serializada

```json
{
  "vector": "fila real de data/amazon_pedidos.csv",
  "referencia": "mediana de 14.411 registros",
  "escala": "IQR de 14.411 registros",
  "hechos": "comparación estricta con P75 del dataset",
  "reglas": "decisiones didácticas del proyecto",
  "secuencia_pod": "escenario controlado; Amazon no registra eventos A/V/F/C"
}
```
