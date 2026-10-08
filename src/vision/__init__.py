"""Módulo de Visión Artificial y Reconocimiento de Imágenes (Corte 2).

¿Por qué se relacionan con 'src/vision/'?
Las Semanas 08–10 abordan el mismo dominio físico: la inspección visual de
paquetes logísticos en estación de reparto. Sin embargo, cada una tiene un
objetivo y una entrada diferentes:
- Semana 08: Aprendizaje automático supervisado (Red Neuronal MLP + Ontología).
- Semana 09: Visión artificial clásica y determinista (Canny + Otsu + Componentes).
- Semana 10: Descriptores numéricos de regiones, intensidad y textura LBP;
  no entrena un clasificador ni diagnostica daños.

================================================================================
📦 BLOQUE SEMANA 08: RECONOCIMIENTO VISUAL, MLP Y ONTOLOGÍA
================================================================================
Núcleo del experimento (orden de revisión recomendado):
  1. src/vision/particion.py       -> Carga 200 imágenes, vectoriza Lanczos 16x16, divide 75/25 por grupos.
  2. src/vision/modelo_mlp.py      -> MLPClassifier (256 -> 64 -> 2), baseline (50%), métricas (48%).
  3. src/vision/ontologia.py       -> Grafo semántico NetworkX, GraphML y regla Human-in-the-Loop.
  4. src/vision/evidencia_mlp.py   -> Persistencia idempotente en PostgreSQL con hashes SHA-256.
  5. src/semana08_reconocimiento.py -> CLI principal de Semana 08 (en src/).

Tubería de datos de soporte del piloto (Semana 08):
  - src/vision/manifiesto.py       -> Contrato e inventario SHA-256 de las 200 imágenes del piloto.
  - src/vision/auditoria.py        -> Validación de integridad PNG, RGB, 960x540 y ausencia de nulos.
  - src/vision/almacenamiento.py   -> Lectura segura desde el volumen privado en disco.
  - src/vision/importacion.py      -> Carga de las 200 imágenes a la tabla 'imagenes' de PostgreSQL.
  - src/vision/asociacion.py       -> Asociación simulada de paquetes a paradas de Amazon Last Mile.
  - src/vision/seed.py             -> Sembrado inicial de datos del piloto.

Integración Semana 08:
  - API:       api/routers/modelo_visual.py
  - Dashboard: dashboard/src/views/MlpView.jsx

================================================================================
🔍 BLOQUE SEMANA 09: CARACTERÍSTICAS, CONTORNOS Y SEGMENTACIÓN CLÁSICA
================================================================================
Núcleo de visión clásica:
  1. src/vision/escena_semana09.py -> Generador determinista de la escena sintética 3D (data/imagen_proyecto.png).
  2. src/semana09_vision.py        -> CLI principal: Canny (sigmas 1, 2, 4), Otsu (t=105) y 8-conectividad (en src/).

Integración Semana 09:
  - API:       api/routers/vision_semana09.py (Valida SHA-256 de entrada; HTTP 503 si cambia).
  - Dashboard: dashboard/src/views/Semana09View.jsx (Laboratorio, Código, Informe).
  - Pruebas:   tests/test_semana09_vision.py

================================================================================
▦ BLOQUE SEMANA 10: REGIONES, INTENSIDAD Y TEXTURA DE PAQUETES
================================================================================
Núcleo del experimento (orden de revisión recomendado):
  1. src/vision/manifiesto.py      -> Contrato y hashes de los 200 originales sintéticos.
  2. src/vision/particion.py       -> Reutiliza la partición por grupo de Semana 08;
                                     150 entrenamiento / 50 prueba reservada.
  3. src/semana10_texturas.py      -> CLI principal: Otsu, regiones de 8 vecinos,
                                     32 bins de intensidad, LBP uniforme (18 bins)
                                     y vector 53D por imagen de entrenamiento.

Evidencia versionada en artifacts/:
  - semana10_resultados.json       -> Configuración, IDs, métricas, hashes y dos ejemplos.
  - semana10_features.npy         -> Matriz 150 x 53, en orden de IDs del JSON.
  - semana10_comparacion.png       -> Figura técnica completa y reproducible.
  - semana10_{danado,intacto}_{gris,mascara}.png
                                  -> Imágenes y máscaras individuales de los dos ejemplos.

Integración Semana 10:
  - API:       api/routers/vision_semana10.py (solo lectura, valida hashes).
  - Dashboard: dashboard/src/views/Semana10View.jsx y Semana10Charts.jsx
               (Ambos / Dañado / Intacto; Laboratorio, Código, Informe).
  - Informe:   reports/semana10.md
  - Estudio:   docs/guia-estudio-semana-10-regiones-intensidad-textura.md
  - Pruebas:   tests/test_semana10_texturas.py y
               dashboard/src/views/Semana10View.test.jsx

Límite: Otsu también segmenta la banda transportadora. Regiones conectadas no
equivalen a paquetes ni a daños; ningún descriptor autoriza despacho.
================================================================================
"""

