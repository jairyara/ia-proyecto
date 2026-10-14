# Proyección Estratégica · Tercer Corte
## Arquitectura de la Torre de Control Logística y Sistema Integrado

> **Documento de referencia para el cierre de semestre (Corte 3)**  
> **Proyecto:** Sistema Inteligente Híbrido para Planificación y Supervisión Logística  
> **Curso:** Inteligencia Artificial · Décimo Semestre  

---

## 1. Visión Ejecutiva: De los Laboratorios a la Operación

Durante los Cortes 1 y 2, el sistema se desarrolló bajo un enfoque modular de **laboratorios aislados** en la plataforma **Órbita** (Semana 02: riesgo supervisado; Semana 04: grafos y A*; Semanas 08, 09 y 10: visión clásica, descriptores de intensidad y texturas LBP).

Para el **Corte 3**, la entrega final exige la transición hacia un **ambiente productivo simulado**. La aplicación se dividirá en dos capas conceptuales y funcionales bien delimitadas:

```text
                                PLATAFORMA INTEGRAL
                                         │
        ┌────────────────────────────────┴────────────────────────────────┐
        ▼                                                                 ▼
[ CAPA 1: LABORATORIOS ACADÉMICOS ]                     [ CAPA 2: TORRE DE CONTROL LOGÍSTICA ]
(Vistas didácticas en Órbita)                           (Plataforma operativa simulada)
• Consulta paso a paso de algoritmos                    • Recepción de paquetes en tiempo real
• Inspección de nodos y frontera A*                     • Subida de fotos / escaneo de paquetes
• Métricas individuales y matrices                      • Auditoría automática de averías físicas
• Sustentación de la rúbrica semanal                    • Orquestación: Visión + Riesgo + Rutas A*
```

---

## 2. Flujo Operativo End-to-End de la Torre de Control

En el centro de operaciones logístico, el operador interactúa con una estación de recepción y despacho continuo:

```text
       1. GENERADOR DE GUÍAS             2. RECEPCIÓN FÍSICA              3. INSPECCIÓN Y RUTEO
   ┌───────────────────────────┐     ┌─────────────────────────┐     ┌──────────────────────────┐
   │ Genera PDF / Imprime guía │ ──► │ Pega en caja real       │ ──► │ Sube foto a la Torre     │
   │ con Tracking ID y destino │     │ o proyecta en pantalla  │     │ de Control Logística     │
   └───────────────────────────┘     └─────────────────────────┘     └────────────┬─────────────┘
                                                                                  │
                                     ┌────────────────────────────────────────────┴──────────┐
                                     ▼                                                       ▼
                       [ ANÁLISIS DE INTEGRIDAD ]                               [ IDENTIFICACIÓN DE GUÍA ]
                       Canny + Otsu + LBP 53D ──► SVC                           OCR / Extracción de Tracking ID
                                     │                                                       │
                                     ▼                                                       ▼
                       Semáforo: ¿Intacto o Averiado?                           Carga pedido de pedidos.csv
                                     │                                                       │
                                     └───────────────────────┬───────────────────────────────┘
                                                             ▼
                                                [ PLANIFICACIÓN Y DESPACHO ]
                                                • Modelo de Riesgo (Logistic / HistGradient)
                                                • Grafo y Ruta óptima con A*
                                                • Validación de Reglas (Cadena de frío / Horarios)
```

### Componentes clave del flujo:

1. **Generador e Impresor de Guías de Prueba:**
   * Módulo en la aplicación que permite generar e imprimir etiquetas estandarizadas (PDF o vista lista para imprimir/celular) con:
     * `Tracking ID` legible y estructurado (ej. `AMZ-BOG-042`).
     * Origen, destino y ventana horaria.
     * Tipo de carga (Estándar, Cadena de Frío, Prioridad Alta).
   * **Propósito en la sustentación:** Permitir una demostración en vivo (*live demo*) con una caja física real donde se capture la foto frente a los jurados.

2. **Percepción e Inspección Visual (Visión por Computador):**
   * **Segmentación de la caja (ROI):** Aislamiento de la caja para eliminar la interferencia de los rodillos de la banda transportadora observada en la Semana 10.
   * **Vector de 53 Descriptores:** 3 métricas de región + 32 bins de intensidad + 18 bins de textura uniforme LBP ($R=2, P=16$).
   * **Clasificador `SVC` (Support Vector Classifier, kernel RBF):** Determina el estado físico (`intacto` vs. `dañado`).
   * **Lectura de la Etiqueta (OCR / Regex):** Extracción automatizada del `Tracking ID` de la guía para vincular la entidad física con la base de datos logística.

3. **Inferencia de Riesgo de Retraso (Supervisado Tabular):**
   * **Modelos en producción:**
     * `LogisticRegression`: Línea base ultrarrápida y explicable para reportar pesos y factores de riesgo al operador.
     * `HistGradientBoostingClassifier`: Ensamble de gradiente para máxima precisión en fronteras no lineales.
   * **Descarte formal del `MLPClassifier`:** No se implementa en producción debido a su mayor latencia, dificultad de calibración y menor explicabilidad frente a los árboles de decisión en tablas.

4. **Planificación y Replanificación Dinámica de Rutas:**
   * Grafo vial basado en paradas reales de Amazon Last Mile.
   * Algoritmo **A*** con heurística admisible (distancia geodésica Haversine).
   * Replanificación automática ante novedades viales o congestión reportada.

5. **Sistema Experto y Restricciones Operativas:**
   * Reglas de negocio auditables: cumplimiento de cadena de frío, capacidades de carga del vehículo y ventanas horarias.

---

## 3. Integración de los 5 Temas Pendientes del Corte 3

Los temas curriculares que se desarrollen durante las semanas restantes del semestre se integrarán bajo una arquitectura desacoplada:

1. **Cada semana conserva su propio Laboratorio Didáctico:** Se crea su submódulo, sus pruebas unitarias y su vista técnica en Órbita para cumplir el 100% de la rúbrica semanal del docente.
2. **Exposición como microservicio interno:** La funcionalidad útil de cada tema se expone mediante funciones puras o endpoints en FastAPI.
3. **Consumo en la Torre de Control:** La Torre de Control invoca el servicio correspondiente como un engranaje más de la operación diaria (por ejemplo, clasificación de novedades, recomendación de contingencias o interfaces conversacionales).

---

## 4. Factibilidad Técnica y Especificaciones de Infraestructura (Specs)

A diferencia de soluciones académicas que requieren hardware prohibitivo, la arquitectura seleccionada está diseñada para cumplir con criterios reales de viabilidad empresarial:

| Criterio | Especificación en Torre de Control | Justificación de Ingeniería |
|---|---|---|
| **Aceleración Hardware** | **Solo CPU (Sin GPU)** | Modelos clásicos (`SVC`, `Logistic`, `HistGradient`) no saturan CPU. Se evita el overhead del bus PCIe en transferencias unitarias. |
| **Specs Mínimos de Servidor** | 2 vCPU, 2 GB RAM, 10 GB Almacenamiento | Permite desplegar el contenedor Monolito (FastAPI + React) en instancias económicas (ej. AWS `t4g.small` o Azure `B2s`). |
| **Costo Operativo Cloud Estimado** | ~15 a 25 USD / mes | Altamente viable para pymes logísticas frente a instancias GPU ($300 - $800 USD/mes). |
| **Latencia de Inferencia** | < 15 ms por paquete | Respuesta instantánea en la estación de escaneo del operario. |
| **Interoperabilidad de Stack** | API REST (FastAPI) + Formatos estándar | Facilita la integración con ERPs corporativos en Java (Spring) o C# (.NET). |

---

## 5. Referencias y Estándares de Arquitectura

Para la fundamentación de las decisiones de diseño y la elaboración de los *Architecture Decision Records* (ADR), el proyecto toma como guía:

* **AWS Prescriptive Guidance — Proceso de ADR:**  
  [AWS ADR Process Guide](https://docs.aws.amazon.com/es_es/prescriptive-guidance/latest/architectural-decision-records/adr-process.html) | [Guía PDF](https://docs.aws.amazon.com/es_es/prescriptive-guidance/latest/architectural-decision-records/architectural-decision-records.pdf#adr-process)
* **AWS Architecture Blog — Prácticas para toma de decisiones efectiva:**  
  [Mastering ADRs](https://aws.amazon.com/blogs/architecture/master-architecture-decision-records-adrs-best-practices-for-effective-decision-making/)
* **Google Cloud Architecture Framework — Decision Records:**  
  [Google Cloud ADR Documentation](https://docs.cloud.google.com/architecture/architecture-decision-records)
* **Repositorio Comunitario ADR / MADR Standard:**  
  [GitHub Architecture Decision Record](https://github.com/architecture-decision-record/architecture-decision-record)
* **Evidencia Empírica de Modelos Tabulares vs. Redes Neuronales (Paper Científico):**  
  Grinsztajn, L., Oyallon, E., & Varoquaux, G. (2022). *Why do tree-based models still outperform deep learning on typical tabular data?* NeurIPS 2022.  
  [Acceso al Paper en arXiv: 2207.08815](https://arxiv.org/pdf/2207.08815)
