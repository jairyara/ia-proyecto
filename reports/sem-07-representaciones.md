# Semana 07 — Representaciones del reconocimiento

> [!NOTE]
> **Trazabilidad académica**  
> **Tema:** Preliminares · Métodos numéricos · Métodos simbólicos · Autómatas  
> **Fuente oficial:** `Semana_07_Representaciones_del_reconocimiento_Clase.pptx` y `Explicacion_Semana_07.md`  
> **Datos del proyecto:** [`data/amazon_pedidos.csv`](../data/amazon_pedidos.csv)  
> **Código:** [`src/representaciones/`](../src/representaciones/) y [`src/representaciones_reconocimiento.py`](../src/representaciones_reconocimiento.py)  
> **Evidencia regenerable:** [`sem-07-representaciones-evidencia.md`](sem-07-representaciones-evidencia.md)

## 1. Objetivo y alcance

Representar el mismo fenómeno de tres maneras y explicar qué conserva y qué
pierde cada una:

1. **Numérica:** vectores y distancia euclidiana.
2. **Simbólica:** hechos discretos y reglas `SI... ENTONCES`.
3. **Secuencial:** estados y transiciones de un Autómata Finito Determinista.

La práctica tiene dos niveles separados. El primero reproduce exactamente el
caso de clase. El segundo aplica los conceptos sobre datos reales de última
milla sin convertir Semana 07 en un problema de entrenamiento: no hay variable
objetivo, ajuste de modelos ni partición train/test.

## 2. Matriz de procedencia

| Elemento | Valor o cantidad | Procedencia | Naturaleza |
|---|---:|---|---|
| Muestra oficial | `[72.0, 0.85, 3.0]` | Presentación Semana 07 | Dato didáctico oficial |
| Referencia oficial | `[70.0, 0.80, 2.0]` | Presentación Semana 07 | Dato didáctico oficial |
| Secuencias `1101`, `1110`, `0001` | 3 | Presentación Semana 07 | Pruebas oficiales |
| Paradas Amazon | 14.411 | ALMRRC 2021, muestra curada de 100 rutas | Datos reales |
| Variables empleadas | 3 de 20 | Columnas observadas del CSV | Datos reales |
| Referencia logística | Mediana de 14.411 filas | Cálculo reproducible | Estadística calculada |
| Escala logística | IQR de 14.411 filas | Cálculo reproducible | Estadística calculada |
| Umbrales simbólicos | P75 de cada variable | Cálculo reproducible | Estadística calculada |
| Consecuencias de reglas | 3 acciones | Definición explícita del proyecto | Decisión de diseño |
| Secuencias POD | `AVF`, `AVC`, `AF`, `AV` | Casos diseñados | Pruebas controladas |

Amazon no registra eventos `A/V/F/C`; por tanto, el AFD POD no se presenta como
evidencia observada. Asimismo, se descartó la telemetría hipotética de
temperatura/carga/retraso que no estaba respaldada por el dataset local.

## 3. Caso oficial de la guía

### 3.1 Representación numérica

$$
x=[72.0,0.85,3.0],\qquad r=[70.0,0.80,2.0]
$$

$$
d(x,r)=\lVert x-r\rVert_2
=\sqrt{2^2+0.05^2+1^2}=2.237
$$

### 3.2 Representación simbólica

```text
Hechos = {temperatura_alta, carga_alta, errores_presentes}
SI {temperatura_alta, carga_alta} ⊆ Hechos
ENTONCES riesgo_termico
```

### 3.3 AFD binario

El autómata acepta cadenas que terminan en `01`.

| Secuencia | Estado final | Resultado |
|---|---|---|
| `1101` | `q2` | `True` |
| `1110` | `q1` | `False` |
| `0001` | `q2` | `True` |

## 4. Adaptación numérica sobre Amazon

Cada parada se representa como:

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

Se exponen dos distancias:

$$
d_{cruda}(x)=\lVert x-\operatorname{mediana}(X)\rVert_2
$$

$$
d_{IQR}(x)=\left\lVert
\frac{x-\operatorname{mediana}(X)}{\operatorname{IQR}(X)}
\right\rVert_2
$$

La primera reproduce la operación de la guía, pero mezcla unidades. La segunda
continúa siendo euclidiana y vuelve comparables las tres escalas. Se usa mediana
e IQR porque volumen y servicio contienen valores extremos. Haversine no aplica
a este vector heterogéneo; permanece en Semana 04 para latitud/longitud.

## 5. Traducción Numérico ↔ Simbólico

Los hechos se activan solo cuando el valor supera estrictamente el P75:

| Condición calculada | Hecho |
|---|---|
| distancia `> 20,4655 km` | `parada_lejana` |
| volumen `> 0,0213 m³` | `volumen_alto` |
| servicio `> 85,0 s` | `servicio_prolongado` |

Distribución al aplicar la traducción sobre las 14.411 paradas:

| Hechos activos | Registros |
|---:|---:|
| 0 | 6.099 |
| 1 | 6.094 |
| 2 | 2.025 |
| 3 | 193 |

Reglas didácticas del proyecto:

```text
parada_lejana ∧ servicio_prolongado → riesgo_desviacion_operativa
volumen_alto ∧ servicio_prolongado → reservar_tiempo_descarga
parada_lejana ∧ volumen_alto → revisar_asignacion_vehiculo
```

Las reglas se evalúan con contención de conjuntos (`issubset`). El sistema
también conserva premisas cumplidas y faltantes para explicar reglas parciales.

## 6. AFD logístico de Proof of Delivery

Formalmente, $M=(Q,\Sigma,\delta,q_0,F)$:

- $Q=\{q_0,q_1,q_2,q_3,q_{fallo}\}$.
- $\Sigma=\{A,V,F,C\}$: Arribo, Validación, Firma y Cancelación.
- $q_0$: vehículo en tránsito.
- $F=\{q_3\}$: entrega auditada.
- Las transiciones inválidas llevan a `q_fallo`, estado absorbente.

| Secuencia controlada | Lectura | Resultado |
|---|---|---|
| `AVF` | Arribo → Validación → Firma | Aceptada |
| `AVC` | Arribo → Validación → Cancelación | Rechazada |
| `AF` | Firma sin validación | Rechazada |
| `AV` | Proceso incompleto | Rechazada |

## 7. Comparación exigida por la guía

| Representación | Qué conserva | Ventajas | Limitaciones | Pérdida de información | Cuándo usarla |
|---|---|---|---|---|---|
| Numérica | Magnitud y cercanía entre vectores | Medible, comparable y compatible con optimización | Depende de escala y referencia | Pierde significado causal y reglas de negocio | Sensores, similitud, anomalías y modelos estadísticos |
| Simbólica | Conceptos, relaciones y justificaciones | Determinista, legible y auditable | Umbrales rígidos; no interpola ruido | Descarta cuánto se excedió un límite | Políticas, restricciones y decisiones explicables |
| Autómata | Orden temporal de eventos | Valida protocolos sin ambigüedad | Crece con estados y no modela magnitudes | Descarta valores numéricos y hechos paralelos | Ciclos de vida, protocolos y patrones secuenciales |

## 8. Validación semanal

1. **REALIZADO:** core modular, caso oficial, datos reales, pruebas, API,
   informe y evidencia existen.
2. **FUNCIONA:** el script procesa 14.411 filas sin entrenamiento y reproduce
   las salidas oficiales; las pruebas cubren límites P75, distancias, reglas y
   estados de fallo.
3. **COINCIDE:** distancia oficial `2.237`, conclusión `riesgo_termico` y AFD
   `True/False/True`, además de la adaptación exigida al dominio.

## 9. Limitaciones y siguiente paso

- P75 describe rareza relativa en la muestra, no una norma logística legal.
- Las reglas son decisiones didácticas, no políticas oficiales de Amazon.
- El AFD POD usa escenarios controlados por ausencia de eventos reales.
- Una siguiente iteración podría incorporar telemetría real o bitácoras POD;
  no se deben inventar esas observaciones para completar el dataset actual.
