# Semana 05 — Evidencia reproducible del sistema híbrido

Generado por `python src/sistema_hibrido.py`. El análisis completo
está en `reports/sem-05-sistema-hibrido.md`.

## Consulta 1
- **Entrada:** El furgón refrigerado perdió temperatura y la carga láctea corre riesgo
- **Reglas activadas:** activar_protocolo_cadena_frio
- **Evidencia recuperada:** Protocolo 1: Control de temperatura y cadena de frío en transporte de perecederos y farmacéuticos; si la temperatura supera los límites o falla el termógrafo, se debe activar refrigeración de emergencia o derivar a centro de acopio cercano.
- **Similitud coseno (TF-IDF):** 0.317
- **Clase predicha (LogisticRegression):** `cadena_frio`

## Consulta 2
- **Entrada:** Accidente grave y congestión vial con cierre en la autopista de reparto
- **Reglas activadas:** replanificar_ruta_alterna
- **Evidencia recuperada:** Protocolo 2: Gestión de congestión y bloqueos viales; ante cierres viales, obras o accidentes de tránsito que excedan 20 minutos de espera, el sistema debe replanificar la ruta con vías alternas evitando cuellos de botella.
- **Similitud coseno (TF-IDF):** 0.245
- **Clase predicha (LogisticRegression):** `rutas_trafico`

## Consulta 3
- **Entrada:** El vehículo superó la capacidad máxima de peso y kilos permitida
- **Reglas activadas:** reasignar_vehiculo_mayor_capacidad
- **Evidencia recuperada:** Protocolo 3: Control de capacidad volumétrica y peso máximo de la flota; ante exceso de kilos o sobrecupo vehicular, se debe reasignar la carga a vehículos de mayor tonelaje o programar un segundo viaje.
- **Similitud coseno (TF-IDF):** 0.437
- **Clase predicha (LogisticRegression):** `capacidad_flota`
