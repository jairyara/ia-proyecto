# Reporte Semana 05 — Marco Tecnológico de la Inteligencia Artificial

> [!NOTE]
> **FICHA DE TRAZABILIDAD ACADÉMICA · SEMANA 05 (EVIDENCIA INDIVIDUAL)**
> - **Tema curricular**: Marco Tecnológico de la IA · Evidencia de ejecución del sistema híbrido.
> - **Problema en última milla**: Validación empírica de consultas operativas de reparto con trazabilidad.
> - **Datos asociados**: [`data/base_conocimiento.txt`](../data/base_conocimiento.txt).
> - **Código ejecutable**: [`src/semana05_sistema_hibrido.py`](../src/semana05_sistema_hibrido.py).
> - **En el Dashboard**: Pestaña *"Semana 05: Sistema híbrido trazable"* -> Visualizador de informe.

**Estudiante:** Catherinne Gutierrez
**Proyecto:** Sistema Inteligente para Logística de Última Milla (Proyecto 8)
**Ejecutable:** `python src/semana05_sistema_hibrido.py`

## Resumen del Sistema Híbrido
El sistema combina tres técnicas del marco tecnológico de la IA sobre consultas operativas:
1. **Sistemas Expertos (Reglas simbólicas):** Evalúa 5 reglas declarativas con detección de palabras detonantes.
2. **Recuperación de Información (TF-IDF + Coseno):** Compara la consulta contra la base de conocimiento de 10 protocolos SOP (`data/base_conocimiento.txt`).
3. **Reconocimiento de Patrones (Clasificación Supervisada):** Predice la categoría logística del incidente con Regresión Logística y distribución de probabilidad.

## Pruebas de Consultas Reales

### Prueba 1
- **Consulta:** "El furgón refrigerado perdió temperatura y la carga láctea corre riesgo"
- **Regla activada:** `activar_protocolo_cadena_frio`
- **Información recuperada:** Protocolo 1: Control de temperatura y cadena de frío en transporte de perecederos y farmacéuticos; si la temperatura supera los límites o falla el termógrafo, se debe activar refrigeración de emergencia o derivar a centro de acopio cercano.
- **Similitud coseno:** `0.317`
- **Clase predicha:** `cadena_frio`

### Prueba 2
- **Consulta:** "Accidente grave y congestión vial con cierre en la autopista de reparto"
- **Regla activada:** `replanificar_ruta_alterna`
- **Información recuperada:** Protocolo 2: Gestión de congestión y bloqueos viales; ante cierres viales, obras o accidentes de tránsito que excedan 20 minutos de espera, el sistema debe replanificar la ruta con vías alternas evitando cuellos de botella.
- **Similitud coseno:** `0.245`
- **Clase predicha:** `rutas_trafico`

### Prueba 3
- **Consulta:** "El vehículo superó la capacidad máxima de peso y kilos permitida"
- **Regla activada:** `reasignar_vehiculo_mayor_capacidad`
- **Información recuperada:** Protocolo 3: Control de capacidad volumétrica y peso máximo de la flota; ante exceso de kilos o sobrecupo vehicular, se debe reasignar la carga a vehículos de mayor tonelaje o programar un segundo viaje.
- **Similitud coseno:** `0.437`
- **Clase predicha:** `capacidad_flota`

## Criterios de Evaluación Verificados
- [x] Base de conocimiento con 10 entradas (mínimo 8 solicitadas).
- [x] Sistema experto con 5 reglas propias del dominio logístico.
- [x] Recuperación con TF-IDF y similitud coseno.
- [x] Clasificador supervisado con 16 ejemplos balanceados en 4 clases.
- [x] 3 consultas de prueba explicables y trazables.
- [x] Reporte generado automáticamente en `reports/semana05.md`.