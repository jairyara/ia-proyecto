# Semana 07 — Representaciones del reconocimiento

> [!NOTE]
> **Tema:** Preliminares · Métodos numéricos · Métodos simbólicos · Autómatas  
> **Datos del proyecto:** [`data/amazon_pedidos.csv`](../data/amazon_pedidos.csv)  
> **Código:** [`src/representaciones/`](../src/representaciones/) y [`src/representaciones_reconocimiento.py`](../src/representaciones_reconocimiento.py)  
> **Evidencia regenerable:** [`sem-07-representaciones-evidencia.md`](sem-07-representaciones-evidencia.md)

## 1. Objetivo y alcance

Representar una operación de última milla de tres maneras complementarias:

1. **Numérica:** vectores de características y distancia euclidiana.
2. **Simbólica:** hechos discretos y reglas `SI... ENTONCES`.
3. **Secuencial:** estados y transiciones de un Autómata Finito Determinista.

Toda la solución se adapta al proyecto logístico. No se incorporan literalmente
los datos, hechos ni patrones secuenciales usados como ejemplo en clase.

## 2. Cambios y commits analizados

| Commit o cambio | Alcance |
|---|---|
| `58f9593` — `feat(representaciones): implementa práctica de semana 7` | Núcleo numérico, simbólico, AFD POD y pruebas. |
| `5bc4c4f` — `feat(dashboard): integra representaciones en corte 2` | API y laboratorio interactivo conectado al mismo núcleo. |
| `d43dc71` — `docs(reportes): documenta evidencia de semana 7` | Informe y evidencia reproducible. |
| `fix(representaciones): alinea entrega con la consigna` | Elimina ejemplos literales, sincroniza código/dashboard, completa el reporte y corrige estándares. |

## 3. Datos, configuración y método

| Elemento | Valor o cantidad | Procedencia | Naturaleza |
|---|---:|---|---|
| Paradas Amazon | 14.411 | ALMRRC 2021, muestra curada de 100 rutas | Datos reales |
| Variables empleadas | 3 de 20 | Columnas observadas del CSV | Datos reales |
| Referencia logística | Mediana de 14.411 filas | Cálculo reproducible | Estadística calculada |
| Escala logística | IQR de 14.411 filas | Cálculo reproducible | Estadística calculada |
| Umbrales simbólicos | P75 de cada variable | Cálculo reproducible | Estadística calculada |
| Consecuencias de reglas | 3 acciones | Definición explícita del proyecto | Decisión de diseño |
| Secuencias POD | `AVF`, `AVC`, `AF`, `AV` | Casos diseñados | Pruebas controladas |

Amazon no registra eventos `A/V/F/C`; por tanto, el AFD POD no se presenta como
evidencia observada. No hay variable objetivo, entrenamiento ni partición
train/test en esta actividad.

## 4. Representación numérica

Cada parada se representa mediante el vector:

$$
x_i=[\text{distancia depósito km},\text{volumen total m}^3,
\text{tiempo servicio s}]
$$

Las tres columnas tienen 14.411 valores válidos y cero nulos.

| Variable | Q1 | Mediana | Q3 | IQR |
|---|---:|---:|---:|---:|
| Distancia al depósito | 9,3660 km | 14,9000 km | 20,4655 km | 11,0995 km |
| Volumen total | 0,0036 m³ | 0,0095 m³ | 0,0213 m³ | 0,0177 m³ |
| Tiempo de servicio | 39,2 s | 56,0 s | 85,0 s | 45,8 s |

El programa calcula la distancia cruda y la distancia normalizada por IQR:

$$
d_{cruda}(x)=\lVert x-\operatorname{mediana}(X)\rVert_2
$$

$$
d_{IQR}(x)=\left\lVert
\frac{x-\operatorname{mediana}(X)}{\operatorname{IQR}(X)}
\right\rVert_2
$$

La distancia cruda mezcla unidades. La normalizada conserva la operación
euclidiana y permite comparar la contribución de las tres características.

## 5. Representación simbólica

Los hechos se activan solo cuando el valor supera estrictamente el P75:

| Condición calculada | Hecho |
|---|---|
| distancia `> 20,4655 km` | `parada_lejana` |
| volumen `> 0,0213 m³` | `volumen_alto` |
| servicio `> 85,0 s` | `servicio_prolongado` |

Distribución sobre las 14.411 paradas:

| Hechos activos | Registros |
|---:|---:|
| 0 | 6.099 |
| 1 | 6.094 |
| 2 | 2.025 |
| 3 | 193 |

Reglas del proyecto:

```text
SI parada_lejana Y servicio_prolongado
ENTONCES riesgo_desviacion_operativa

SI volumen_alto Y servicio_prolongado
ENTONCES reservar_tiempo_descarga

SI parada_lejana Y volumen_alto
ENTONCES revisar_asignacion_vehiculo
```

Las reglas se evalúan mediante contención de conjuntos (`issubset`) y conservan
las premisas cumplidas y faltantes para explicar activaciones parciales.

## 6. Reconocimiento mediante autómata

El AFD logístico valida el protocolo de Proof of Delivery. Formalmente,
$M=(Q,\Sigma,\delta,q_0,F)$:

- $Q=\{q_0,q_1,q_2,q_3,q_{fallo}\}$.
- $\Sigma=\{A,V,F,C\}$: Arribo, Validación, Firma y Cancelación.
- $q_0$: vehículo en tránsito.
- $F=\{q_3\}$: entrega auditada.
- Las transiciones inválidas llevan a `q_fallo`, estado absorbente.

| Secuencia controlada | Lectura | Estado final | Resultado |
|---|---|---|---|
| `AVF` | Arribo → Validación → Firma | `q3` | Aceptada |
| `AVC` | Arribo → Validación → Cancelación | `q_fallo` | Rechazada |
| `AF` | Firma sin validación | `q_fallo` | Rechazada |
| `AV` | Proceso incompleto | `q2` | Rechazada |

## 7. Comparación de representaciones

| Representación | Qué información utiliza | Qué puede reconocer | Ventajas | Limitaciones | Información que puede perderse |
|---|---|---|---|---|---|
| Numérica | Distancia al depósito, volumen, tiempo de servicio, mediana e IQR | Cercanía o desviación de una parada respecto al perfil central | Medible, comparable y compatible con optimización | Depende de la escala y de la referencia elegida | Causas, reglas de negocio y orden de eventos |
| Simbólica | Hechos derivados por P75 y premisas declarativas | Condiciones operativas que activan una conclusión | Determinista, legible y auditable | Umbrales rígidos; no interpola ni modela incertidumbre | Magnitud exacta y cuánto se excedió el límite |
| Autómata | Símbolos POD y orden cronológico de la secuencia | Cumplimiento completo del protocolo de entrega | Valida secuencias sin ambigüedad y conserva una traza | Crece con el número de estados y no modela magnitudes | Valores numéricos y hechos paralelos sin representación secuencial |

## 8. Resultados y validación

El comando siguiente ejecuta las tres representaciones, muestra sus resultados
en consola y regenera la evidencia:

```bash
python -m src.representaciones_reconocimiento
```

Las pruebas cubren distancias, límites P75, reglas activadas/parciales, estados
del AFD, aceptación y rechazo, procedencia y contratos del dashboard.

## 9. Conclusiones, limitaciones y siguiente paso

- Las tres representaciones describen aspectos distintos de una misma entrega;
  ninguna sustituye por sí sola a las demás.
- P75 describe rareza relativa en la muestra, no una norma logística legal.
- Las reglas son decisiones didácticas, no políticas oficiales de Amazon.
- El AFD POD usa escenarios controlados porque el dataset no contiene eventos.
- Una siguiente iteración debe usar telemetría o bitácoras POD reales, sin
  inventar observaciones ausentes del dataset.
