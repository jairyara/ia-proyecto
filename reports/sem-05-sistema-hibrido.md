# Reporte Técnico — Sistema Híbrido de Trazabilidad (Reglas + TF-IDF + Clasificación)

**Curso:** Inteligencia Artificial · 10.º semestre · Proyecto 8 (Sistema Inteligente para Logística)  
**Tema:** Marco tecnológico de la IA · Sistemas expertos · Ingeniería del conocimiento · Recuperación de información · Reconocimiento de formas · PLN  
**Módulos:** `src/hibrido/sistema.py`, `src/sistema_hibrido.py`  
**Datos:** `data/base_conocimiento.txt` (10 protocolos SOP) y 16 ejemplos etiquetados en 4 clases operativas  

---

## 1. Arquitectura del sistema híbrido

El sistema responde consultas operativas en lenguaje natural combinando tres técnicas del marco tecnológico sobre la **misma entrada normalizada** (minúsculas, sin tildes):

```text
consulta del operador
        │
        ▼  normalización (PLN)
┌─────────────────────────────────────────────┐
│ 1. Reglas expertas  → acción + detonante    │
│ 2. TF-IDF + coseno  → protocolo + similitud │
│ 3. Regresión logística → clase + probabilidad│
└─────────────────────────────────────────────┘
        │
        ▼
respuesta trazable (auditable)
```

| Técnica | Rol en la decisión | Fortaleza | Salida |
|---|---|---|---|
| **Sistema experto** | Disparar protocolos de contingencia | Determinista y auditable | Acción + palabra detonante |
| **Recuperación TF-IDF** | Fundamentar en el SOP documental | Evidencia textual cuantificada | Documento + similitud coseno |
| **Clasificador supervisado** | Categorizar el incidente | Generaliza lenguaje no estructurado | Clase + distribución de probabilidad |

A diferencia del script de clase (reglas como `lambda` anónimas), las reglas se declaran como **datos estructurados** (`Regla(accion, palabras, descripcion)`), de modo que el sistema no solo indica *qué regla se disparó*, sino también *qué palabra de la consulta la activó* — evidencia clave para la sustentación.

---

## 2. Base de conocimiento (ingeniería del conocimiento)

Diez procedimientos operativos estandarizados (SOP) del dominio logístico, versionados en `data/base_conocimiento.txt`:

1. Cadena de frío y monitoreo de temperatura en ruta.
2. Congestión, cierres viales y bloqueos en carretera.
3. Control de pesaje, sobrecupo y balance de carga.
4. Ventanas horarias y políticas de entrega tardía.
5. Despacho express para clientes prioritarios.
6. Destinatario ausente o dirección inaccesible.
7. Transporte y estiba de mercancías frágiles.
8. Restricciones de movilidad urbana (zonas de bajas emisiones).
9. Asistencia técnica ante fallas mecánicas en ruta.
10. Prueba de entrega (POD) y remisión digital.

---

## 3. Reglas expertas del dominio

| Regla | Palabras clave | Acción operativa en el proyecto |
|---|---|---|
| `activar_protocolo_cadena_frio` | frio, temperatura, refrigerad, congelad | Alarma térmica: desvío a punto frío o refrigeración de auxilio |
| `replanificar_ruta_alterna` | bloqueo, cierre, trafico, congestion, accidente | Invoca A* excluyendo la arista cerrada |
| `reasignar_vehiculo_mayor_capacidad` | peso, capacidad, sobrecupo, kilos, tonelaje, sobrecarga | Divide la orden o reasigna un móvil |
| `renegociar_ventana_entrega` | ventana, horario, retraso, tarde, plazo | Notifica y actualiza el cronograma |
| `escalar_despacho_prioritario` | urgente, prioritario, emergencia, express | Antepone en la cola de despacho con flota directa |

---

## 4. Clasificador supervisado

Pipeline `TfidfVectorizer` + `LogisticRegression(max_iter=1000, random_state=42)`, entrenado con 16 casos balanceados (4 por clase):

- `cadena_frio` — incidencias térmicas y conservación de productos.
- `rutas_trafico` — novedades de movilidad e incidentes viales.
- `capacidad_flota` — restricciones de peso, volumen y flota.
- `entregas_clientes` — ventanas horarias, prioridad y atención al destinatario.

---

## 5. Evidencia de ejecución (consultas de la guía)

Reproducible con `python -m src.sistema_hibrido` (salida completa en `reports/sem-05-sistema-hibrido-evidencia.md`):

| # | Consulta | Regla disparada | Protocolo recuperado | Similitud | Clase |
|---|---|---|---|---|---|
| 1 | «El furgón refrigerado perdió temperatura y la carga láctea corre riesgo» | `activar_protocolo_cadena_frio` (detonantes: *temperatura, refrigerad*) | Protocolo 1 · cadena de frío | 0.317 | `cadena_frio` |
| 2 | «Accidente grave y congestión vial con cierre en la autopista de reparto» | `replanificar_ruta_alterna` (detonantes: *accidente, congestion, cierre*) | Protocolo 2 · contingencias viales | 0.245 | `rutas_trafico` |
| 3 | «El vehículo superó la capacidad máxima de peso y kilos permitida» | `reasignar_vehiculo_mayor_capacidad` (detonantes: *capacidad, peso, kilos*) | Protocolo 3 · control de carga | 0.437 | `capacidad_flota` |

---

## 6. Limitaciones del sistema

1. **Sensibilidad al vocabulario:** sinónimos no indexados en las reglas ni en el vocabulario TF-IDF degradan la recuperación (mitigación: ampliar `palabras` y los SOP con el léxico real de los operadores).
2. **Solapamiento de reglas:** una consulta compuesta puede disparar varias reglas a la vez; falta un mecanismo de prioridad por criticidad.
3. **Dataset acotado:** con 16 ejemplos, la regresión logística generaliza dentro del dominio cerrado pero puede fallar con lenguaje coloquial atípico.
4. **Sin contexto conversacional:** cada consulta se evalúa aislada, sin memoria de la jornada ni del estado del vehículo.

---

## 7. Conexión con el Corte 2 (`v2.0.0`)

El diccionario de trazabilidad (reglas + evidencia + similitud + clase) actuará como **validador de planes**: cuando A* proponga una secuencia de entrega, el motor híbrido verificará que no se violen las restricciones operativas (cadena de frío, capacidad, ventanas) y dejará registro de auditoría de cada validación.

---

## 8. Verificación de las 3 Condiciones del Curso

1. **REALIZADO:** módulo `src/hibrido/`, base de conocimiento con 10 SOP, 5 reglas, 16 ejemplos, 3 consultas de prueba y este informe.
2. **FUNCIONA:** `python -m src.sistema_hibrido` ejecuta sin errores y reproduce la evidencia; 100% de las pruebas unitarias en verde.
3. **COINCIDE:** integra reglas expertas, ingeniería del conocimiento, recuperación TF-IDF + coseno, clasificación supervisada y PLN con trazabilidad completa, adaptado al dominio del proyecto (logística de última milla).
