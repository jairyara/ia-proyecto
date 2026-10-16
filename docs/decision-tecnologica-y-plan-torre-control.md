# Plan de ejecución y decisión tecnológica · Torre de Control, Corte 3

**Fecha:** 2026-10-14  
**Estado:** Plan de ejecución aprobado en alcance y supuestos de carga; decisiones de modelo y capacidad definitiva sujetas a medición. No sustituye el ADR de Semana 11.  
**Alcance:** `ia-proyecto`. `ia-semestre` es referencia académica, no fuente de decisiones de producción.

> **Avance de Semana 11 (2026-10-14):** el cuarteto se ejecutó sobre
> `data/amazon_pedidos.csv`: [`benchmark.csv`](../artifacts/benchmark.csv),
> [informe](../reports/semana11.md) y [ADR-011](../reports/semana11_adr.md).
> Forest gana al **imitar la etiqueta heurística**, pero no se sustituye la regla
> explícita que la generó ni se afirma predecir retrasos observados. El resto de
> este documento es un **plan**, no una Torre ya implementada ni una capacidad
> de servidor probada.

## 1. Decisiones que se deben cerrar con evidencia

La Semana 11 comparó **cuatro modelos** (`logistic`, `forest`, `mlp`, `hist`) sobre las **paradas Amazon ya curadas** del proyecto, no sobre una copia del laboratorio de `ia-semestre`. Los tres primeros proceden de la guía docente; `hist` es un retador tabular. Tras excluir 100 estaciones, 14.311 entregas comparten protocolo y rutas reservadas. El ADR enlaza resultados, distingue hechos medidos de hipótesis y separa el ganador académico de una decisión operativa. La comparación de dígitos de la guía sirve de referencia conceptual, **no** decide el modelo logístico.

El paper de Grinsztajn, Oyallon y Varoquaux (NeurIPS 2022) fundamenta considerar modelos de árboles frente a redes neuronales en datos tabulares medianos; **no prueba** que `HistGradientBoostingClassifier` gane a `RandomForestClassifier`. En este benchmark Forest obtuvo F1 0,9980 frente a Hist 0,9920 sobre una **etiqueta derivada de reglas**. La casi perfección confirma principalmente que los árboles pueden recuperar esos umbrales; no valida demoras reales.

El ADR seguirá un ciclo **Propuesto → Revisado → Aceptado**: contexto y restricciones, alternativas, criterios, evidencia reproducible, decisión, consecuencias, riesgos, propietario y fecha. Una nueva evidencia que invalide una decisión aceptada generará un ADR sucesor, sin borrar el historial.

**Protocolo ejecutado de Semana 11:** `data/amazon_pedidos.csv`, 14.311 `Dropoff`, siete variables conocidas antes del despacho y `retrasado_estimado` como objetivo heurístico. Un pliegue de `StratifiedGroupKFold(4)` reservó 3.509 entregas de 24 rutas; 10.802 de 76 rutas quedaron en train. Cinco pliegues agrupados internos eligieron umbrales F2; el preprocesamiento se ajustó dentro de cada pipeline y el test se evaluó una vez. `artifacts/benchmark.csv` tiene cuatro filas y `semana11_benchmark.json` registra hash, semilla, versiones y matrices. Los tiempos locales no son constantes universales. `data/pedidos.csv` permanece para prácticas anteriores, **no como segundo benchmark de Semana 11**. La etiqueta Amazon es heurística, no retraso observado.

## 2. Lenguaje y forma de despliegue: decisión para el MVP

**Problema:** elegir cómo llevar a producción simulada los modelos, visión, reglas y ruteo existentes, y cómo ofrecer el producto a clientes cuyo ERP/TMS esté construido en otro lenguaje.

**Restricciones verificables:** conservar los modelos y librerías ya usados; permitir consumir capacidades desde Java, C#, Go u otro cliente; registrar decisiones; instalar y recuperar el servicio de manera repetible; medir latencia del flujo completo y memoria bajo carga. No se ha demostrado una necesidad de cientos de solicitudes por segundo como en el caso ITCDrive de Ingeniería de Software III.

| Alternativa | Ventaja en este proyecto | Costo o riesgo | Juicio para el MVP |
|---|---|---|---|
| **Python + FastAPI** para dominio e inferencia | Reutiliza `scikit-learn`, visión, A*, reglas y API actual; reduce traducciones y tiempo de entrega | Hay que medir concurrencia CPU y memoria por proceso/modelo | **Elegida para el MVP** |
| **Go** como backend nuevo | Buen perfil de concurrencia y despliegue | Reimplementar o mantener un servicio Python aparte para los modelos; más interfaces y operación | Solo si pruebas muestran cuello de botella real |
| **Rust** como backend nuevo o extensión nativa | Control de recursos y seguridad de memoria | Reescritura o puente hacia Python, curva de aprendizaje y doble cadena de construcción | Reservar para un cuello de botella medido |
| **Java/C#** como backend nuevo | Alineación posible con ERP de un cliente | No elimina la necesidad de servir los modelos Python; aumenta el alcance del semestre | Integrar como **cliente** de la API, no reescribir el núcleo |

**Decisión aprobada para el MVP:** comenzar como **monolito modular** en el backend FastAPI existente, con contratos internos claros, Órbita como interfaz y persistencia/auditoría compartida. La razón principal es **reducir riesgo de integración y de divergencia de modelos**: `ia-proyecto` ya implementa en Python aprendizaje supervisado, visión, A*, reglas y API. Un backend Go/Rust seguiría necesitando un servicio Python para los modelos o una reimplementación cuya equivalencia habría que demostrar. No se afirma que Python tenga mejor throughput o latencia. La carga propuesta es pequeña; primero se miden sus límites reales. La elección del lenguaje se revisa si se incumplen los objetivos de rendimiento tras optimizar el pipeline, procesos y recursos.

Publicar una **API HTTP versionada y descrita con OpenAPI**. Si un cliente opera en Java, C#, Go o Rust, su sistema consume la API y conserva sus propias transacciones; no se exige portar su ERP ni reescribir el modelo. Un adaptador específico del cliente mapea identificadores, estados y autenticación al contrato de Torre. Solo extraer inferencia o procesamiento de imágenes a un microservicio desplegado por separado cuando mediciones o requisitos de aislamiento lo justifiquen. La independencia de lenguaje se obtiene por el **contrato de red**, no por multiplicar servicios prematuramente.

**Contrato mínimo para terceros:** versión de API; identificación y autorización; esquema de pedido y guía; `tracking_id` externo y correlación interna; estados y errores tipados; idempotencia al registrar recepción/eventos; tiempo de espera y reintento definido; versión de modelo y trazabilidad en la respuesta. Datos de clientes reales requieren tratamiento de seguridad y retención acordados contractualmente; la demo solo usará datos simulados.

### Matriz de decisión adaptada al proyecto

Los **requisitos excluyentes** son: preservar o reproducir fielmente el comportamiento de los modelos, cumplir el contrato HTTP para clientes externos y superar la prueba de carga del §4. Todas las opciones podrían hacerlo con arquitecturas distintas; ninguna recibe aprobación de rendimiento sin ensayo. Las calificaciones siguientes son **juicios de ingeniería sobre el código actual y esfuerzo de integración**, no benchmarks de velocidad. Escala 1–5; mayor es mejor.

| Criterio | Peso | Python/FastAPI | Go + servicio ML | Rust + servicio ML | Java/C# + servicio ML |
|---|---:|---:|---:|---:|---:|
| Reutilización fiel del pipeline ML/visión actual | 30 % | 5 | 2 | 2 | 2 |
| Plazo de entrega y capacidad del equipo | 20 % | 5 | 2 | 1 | 3 |
| Interoperabilidad vía contrato HTTP | 15 % | 5 | 5 | 5 | 5 |
| Operación y número de componentes | 15 % | 4 | 3 | 3 | 3 |
| Margen **esperado**, no medido, de rendimiento | 20 % | 3 | 5 | 5 | 4 |
| **Total ponderado / 5** | **100 %** | **4,45** | **3,20** | **3,00** | **3,20** |

**Fundamento de las notas:** Python puntúa alto en reutilización/plazo porque los módulos y las dependencias ya existen en este repositorio; Go, Rust y Java/C# exigen agregar una segunda implementación o un servicio ML Python. Todos pueden consumir/exponer HTTP. La ventaja de rendimiento de Go/Rust es una **hipótesis favorable**, no una medición de esta aplicación. La nota de Python en operación reconoce el costo de memoria por worker que carga modelos. **Sensibilidad:** si rendimiento pesara 50 % (reutilización 15 %, plazo 5 %, interoperabilidad 15 %, operación 15 %), Go pasaría a **4,10** y Python a **3,85**: la elección cambiaría. Por eso se exige una prueba de carga y se conserva una frontera de API que permita extraer componentes después. Las cifras de este ejercicio no son una promesa comercial.

El taller de Ingeniería de Software III aporta **el formato** (problema, restricciones, alternativas, pesos, sensibilidad, riesgos y fuentes), no su resultado. La elección de Go para ITCDrive responde a un motor de precios y una carga diferentes; no se trasplanta a la Torre. Tampoco se descalifica Python con la afirmación absoluta de que «no puede usar varios núcleos»: el despliegue puede usar varios procesos y Python 3.14 tiene una compilación opcional *free-threaded*, cuya compatibilidad con extensiones debe verificarse. Para este MVP se usará la configuración normal del proyecto y se medirán procesos, CPU y memoria.

**Disparadores de revisión:** incumplimiento repetido del objetivo p95 con la carga aprobada; uso sostenido de CPU >80 % o memoria >75 %; necesidad de escalar visión independientemente; o un requisito contractual de aislamiento/throughput que no se resuelva con el despliegue actual. Primero se perfila y corrige el componente causante; solo después se evalúa extracción a otro servicio/lenguaje mediante nuevo ADR.

## 3. Arquitectura objetivo de la simulación

```text
Operador en Órbita / ERP cliente
             │ HTTP + OpenAPI
             ▼
API Torre de Control (autenticación, validación, estado, auditoría)
             │
             ├─ Guías y recepción ── tracking ID; OCR opcional + ingreso manual verificado
             ├─ Inspección visual ── imagen → ROI/53D → SVC candidato → revisión humana
             ├─ Riesgo heurístico ── regla versionada; modelo académico como retador
             ├─ Reglas duras ── capacidad, frío, horarios y autorización
             └─ Rutas y eventos ── A*; cierre vial/pedido nuevo → replanificación
             │
             ▼
Persistencia: pedido, guía, imagen/evidencia, evento, estado, decisión y versión
```

**Caso mínimo completo:** crear o seleccionar pedido → generar guía → registrar recepción → asociar foto/guía (OCR o respaldo manual) → clasificar integridad con resultado e incertidumbre → calcular riesgo → comprobar reglas → proponer ruta → confirmar/rechazar por operador → simular novedad → replanificar o detener → consultar bitácora. Una predicción no debe saltarse una restricción dura ni autorizar automáticamente el despacho. Si OCR no lee, el operador ingresa y confirma el código. Si imagen/modelo falla o la confianza es insuficiente, el paquete pasa a revisión manual. Ambas vías quedan auditadas.

El descriptor visual 53D de Semana 10 es **exploratorio y sintético**. Antes de usarlo en decisiones, hay que entrenar un clasificador, evaluar el conjunto reservado por grupos, medir falsos negativos de daño y definir abstención. La demo puede usar datos e imágenes simulados, identificados como tales; no se afirmará validez para paquetes reales sin un estudio adicional.

**Clasificador visual previsto:** `SVC` con kernel RBF, dentro de un pipeline `StandardScaler → SVC`, entrenado para `intacto` frente a `dañado` sobre los vectores 53D de Semana 10. El vector actual contiene **3 medidas de regiones segmentadas con Otsu + 32 bins de intensidad + 18 bins LBP**. **Canny se calcula en Semana 9 para mostrar/analizar bordes, pero no forma parte del vector 53D actual**; si se decide usarlo como característica, habrá que versionar el descriptor y repetir entrenamiento/evaluación. `SVC` es una **hipótesis de modelo**, no una clasificación ya implementada: se contrastará al menos con una línea base simple, se ajustará solo con entrenamiento/validación y se evaluará una sola vez sobre los 50 casos reservados por grupos. Documentar recall de paquetes dañados, falsos negativos, matriz de confusión y tiempos; si el resultado no alcanza el umbral acordado, la Torre enviará a revisión humana en vez de automatizar cuarentena o despacho.

## 4. Perfil de carga aprobado y dimensionamiento inicial

**Escenario de diseño del MVP, aprobado como supuesto y no como demanda observada:** 5–10 operadores simultáneos, hasta 500 pedidos por jornada de 8 horas, una hora pico de hasta 150 pedidos, ráfagas de 3 solicitudes API/s, una foto por pedido de hasta 2 MB y retención operativa de fotos originales por 30 días. La media es 62,5 pedidos/h; el pico representa 2,4 veces esa media. Se ensayarán además eventos de replanificación y fallos de OCR con ingreso manual.

**Almacenamiento:** 500 fotos/día × 2 MB × 30 días = **30 GB de originales** si todos los pedidos llegan al máximo; no incluye derivados, BD ni copias. Reservar inicialmente **80–100 GB de almacenamiento persistente** para la demo/piloto en un solo host, con vigilancia de crecimiento y política de borrado/archivo a los 30 días. Las copias de seguridad se almacenarán **fuera** del volumen principal y se probará restauración. Si se retienen fotos por más tiempo o se aceptan múltiples fotos, recalcular antes de desplegar. La cifra anterior de 10 GB no sirve para este escenario.

| Entorno | Configuración inicial para probar | Qué debe medirse antes de declararlo suficiente |
|---|---|---|
| Desarrollo local | Compose actual, sin promesa de capacidad; PostgreSQL se activa con perfil `persistencia` y contraseña configurada | Pruebas funcionales, integridad de volúmenes y arranque repetible |
| Demo/piloto en un host | **4 vCPU, 8 GB RAM, 80–100 GB persistentes** para API/React, PostgreSQL y fotos; una instancia inicial de API | Arranque, RSS/pico, carga de modelos, fotos de 2 MB, p50/p95/p99, errores, recuperación y restauración |
| Piloto de cliente con BD separada | Misma imagen/versiones; base de datos y almacenamiento de imágenes separados si volumen o aislamiento lo exige | Capacidad real, CPU, RAM por proceso, I/O, crecimiento de evidencias y costo total |
| Escalado | Más réplicas o servicio de inferencia/visión separado **solo tras detectar el cuello de botella** | Comparación antes/después, costo total, consistencia de estado e idempotencia |

**Objetivos de aceptación para la prueba, no resultados observados:** sin pérdidas ni duplicados de pedidos en la carga propuesta; 0 errores no controlados en el recorrido E2E de los tres escenarios; p95 <1 s para el tramo sin imagen (riesgo + reglas + ruta + persistencia) y p95 <10 s desde foto ya recibida hasta resultado de inspección/OCR o derivación manual. Registrar también p99, cola y tasa de abstención. Si un objetivo falla, el resultado se documenta y se perfila antes de declarar el servidor suficiente. El escenario de carga incluye al menos 150 casos en una hora, ráfagas de 3 solicitudes/s y fotos de tamaño máximo.

La propuesta anterior de 2 vCPU/2 GB, inferencia <15 ms y USD 15–25/mes no tiene aún una prueba E2E ni cotización vigente: **no** se afirmará en el ADR. Se medirán por separado inferencia del modelo y tiempo de **recepción a decisión**. Cada proceso de API que carga modelos consume memoria propia; no aumentar workers sin medir. El Compose actual integra React compilado y FastAPI en `dashboard`, ofrece PostgreSQL como perfil `persistencia`, usa volúmenes y todavía no fija límites de CPU/RAM. Antes de una demo persistente habrá que activar/configurar la BD, fijar límites y observar OOM, reinicios y disco. El costo cloud requerirá región, arquitectura de CPU, BD, almacenamiento, tráfico y fecha de cotización concretos.

## 5. Secuencia de construcción y criterios de cierre

| Semana | Incremento verificable |
|---|---|
| **11** | Benchmark Amazon de cuatro modelos sobre etiqueta heurística; CSV, pruebas, informe y ADR que conserva la regla explícita para simulación. No valida retrasos observados ni desarrolla aún toda la Torre. |
| **12** | Primer flujo desde pedido existente a riesgo → reglas → A* → decisión persistida; contrato API y estados de caso. Cierre del Corte 2. |
| **13** | Generación de guía y recepción vinculada por tracking ID; ingreso manual auditado. |
| **14** | Captura de foto, almacenamiento y asociación a pedido; prototipo OCR que nunca sea punto único de fallo. |
| **15** | Entrenar y contrastar `StandardScaler → SVC(RBF)` sobre 53D frente a línea base; evaluar los 50 casos reservados por grupos, fijar abstención y revisión manual. |
| **16** | Eventos simulados, replanificación, condición de parada y bitácora completa. |
| **17** | Pruebas E2E y de carga, medición de recursos/latencia, fallos controlados y tres escenarios de demostración. |
| **18** | Torre funcional demostrable, ADR/limitaciones actualizados, reporte final y procedimiento reproducible de instalación. |

**Puertas de aceptación:** ninguna semana se declara cerrada solo por tener pantalla; debe existir prueba automatizada, evidencia persistida y una ruta de error explicable. La Semana 18 exige que los tres escenarios puedan ejecutarse sin depender de OCR perfecto ni de servicios externos inestables.

## 6. Pendientes que requieren validación del equipo

1. **Etiqueta real de retraso:** conseguir hora prometida y hora efectiva de llegada/entrega, definir qué cuenta como retraso, censuras, cancelaciones y origen auditable. El código de `retrasado_estimado` incluye `secuencia_real`, aunque **en el CSV actual esa cláusula no añade positivos exclusivos**; las otras dos reproducen la etiqueta completa. Es una heurística, no verdad terreno; el benchmark de Semana 11 solo evalúa su reproducción.
2. **Momento de predicción y variables disponibles:** separar lo conocido antes del despacho de lo observado durante/después de la ruta; decidir si la Torre predice al planear, al salir o tras cada evento. No permitir `secuencia_real` como entrada de una predicción previa al despacho. Revisar posibles proxies y fuga por ruta, estación, fecha, zona y eventos futuros.
3. **Generalización y costo operativo:** validar con rutas/días posteriores y, cuando haya etiquetas observadas, con datos de otra operación; medir prevalencia, calibración, falsos negativos, falsas alertas y costo de revisión humana. Un buen resultado al imitar la heurística no aprueba uso productivo.
4. **Política de clasificación visual:** umbral de abstención y costo aceptable de pasar un paquete dañado como intacto. Debe definirse antes de activar decisiones visuales; las 200 imágenes no se unen causalmente a las paradas Amazon.
5. **Perfil contractual de un cliente real:** datos/operaciones permitidos, autenticación, retención y residencia de datos. El MVP simulado no presupone un contrato comercial concreto.
6. **Responsables de revisión/aceptación de cada ADR** y fecha para congelar la demo.
7. **Servidor/proveedor y precio definitivos:** requieren resultados de carga y cotización vigente; **no bloquean** la implementación local.

## Fuentes

- Material de Ingeniería de Software III: `../ing-soft-3/14-10/Lab. taller-toma de decisiones.pdf`, `Plantilla_Informe_Decision_Tecnologica.pdf`, `informe-decision-itcdrive.md` (consultados 2026-10-14). La carpeta real es `14-10`, no `14-10-26`.
- [Grinsztajn et al., NeurIPS 2022 — modelos tabulares](https://proceedings.neurips.cc/paper_files/paper/2022/hash/0378c7692da36807bdec87ab043cdadc-Abstract-Datasets_and_Benchmarks.html).
- [scikit-learn — comparación Random Forest / HistGradientBoosting](https://scikit-learn.org/stable/auto_examples/ensemble/plot_forest_hist_grad_boosting_comparison.html).
- [scikit-learn — validación y separación del conjunto de prueba](https://scikit-learn.org/stable/modules/cross_validation.html).
- [AWS Prescriptive Guidance — proceso y estados de ADR](https://docs.aws.amazon.com/prescriptive-guidance/latest/architectural-decision-records/adr-process.html).
- [OpenAPI Specification — contrato HTTP independiente del lenguaje](https://spec.openapis.org/oas/v3.1.1.html).
- [FastAPI — procesos, contenedores y memoria](https://fastapi.tiangolo.com/deployment/docker/).
- [Docker — límites de CPU y memoria](https://docs.docker.com/engine/containers/resource_constraints/).
- [scikit-learn — ecosistema de aprendizaje automático Python](https://scikit-learn.org/stable/getting_started.html).
- [Go — modelo de concurrencia](https://go.dev/doc/effective_go#concurrency).
- [Python 3.14 — compilación opcional sin GIL y compatibilidad de extensiones](https://docs.python.org/3.14/howto/free-threading-python.html).
- [Rust — garantías y límites de seguridad de memoria](https://doc.rust-lang.org/reference/unsafety.html).
