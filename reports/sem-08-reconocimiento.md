# Semana 8 — Reconocimiento, evidencia y significado

**Dataset:** piloto visual auditado, 200 imágenes sintéticas `side` (100 por clase). No son fotografías de envíos Amazon.  
**Partición:** 150 entrenamiento / 50 prueba, estratificada por grupo, semilla 20260925.  
**Entrada:** gris 16×16, 256 intensidades normalizadas a [0,1].  
**Modelo:** `MLPClassifier(hidden_layer_sizes=(64,), max_iter=400, random_state=42)`.  
**Versión:** `mlp-visual-v1`; SHA-256 del manifiesto `ef62b04ff8cda7cb0b69a4525f7daf77a8d47b3f0a5bbf3b261e040ae3f12ca7`.  
**Registro PostgreSQL:** realizado.

## Evaluación reservada

| Métrica | Resultado |
|---|---:|
| Accuracy MLP | 0.480 |
| Accuracy línea base mayoritaria | 0.500 |
| F1 dañado | 0.500 |
| F1 intacto | 0.458 |

Matriz de confusión; filas reales y columnas predichas en orden `danado`, `intacto`:

| Real / predicha | Dañado | Intacto |
|---|---:|---:|
| Dañado | 13 | 12 |
| Intacto | 14 | 11 |

**Convergencia:** se observó advertencia; el optimizador llegó al límite de iteraciones.
**Interpretación:** el piloto es didáctico. Si el MLP no supera la línea base, no existe sustento para automatizar decisiones operativas. Incluso si la superase, el tamaño y origen sintético limitan la generalización.

## Evidencia y semántica

- Los originales y etiquetas siguen inmutables; `modelo_mlp_logistica.json` contiene parámetros, IDs exactos por partición, métricas y predicciones de prueba.
- `modelo_mlp_logistica.pkl` conserva el modelo entrenado; solo deben cargarse artefactos propios verificados por hash.
- La ontología logística GraphML contiene 13 relaciones, incluidas las de una imagen de prueba. Es un grafo semántico didáctico, no un razonador formal ni autorización automática de despacho.
- PostgreSQL conserva imágenes y metadatos de origen; al ejecutar `--registrar`, añade modelo, partición y predicciones de prueba sin reetiquetar imágenes.
- Las asociaciones entre el piloto y las paradas Amazon siguen siendo simuladas.

## Reproducción

```bash
python -m alembic upgrade head
python -m src.semana08_reconocimiento --registrar
```

La primera línea es una operación administrativa explícita. El comando de entrenamiento no migra ni importa datos automáticamente y falla si el piloto auditado o el registro PostgreSQL no coincide.

## Correspondencia con la guía

La guía de clase usa `load_digits`, SQLite y nombres de artefacto genéricos. Se conservaron los objetivos evaluables —reconocer, persistir evidencia y representar significado— mediante decisiones del proyecto:

| Objetivo de la rúbrica | Adaptación y motivo | Evidencia |
|---|---|---|
| MLP que reconoce patrones y reporta accuracy | Clasificación de paquetes `intacto`/`danado` en lugar de dígitos para mantener el dominio logístico | Partición 150/50, accuracy, baseline, matriz y `modelo_mlp_logistica.pkl` |
| Base de imágenes y metadatos consultables | PostgreSQL con Alembic en lugar de SQLite para no mantener dos fuentes de verdad | `imagenes`, `modelos_visuales`, `muestras_modelo_visual` y API de lectura |
| Guardar y recuperar originales | Archivos en volumen privado persistente y hashes/referencias en PostgreSQL; no duplicar bytes como Base64 | Manifiestos, SHA-256, almacenamiento y endpoint por ID |
| Ontología con relaciones del dominio | GraphML logístico con conceptos propios y vínculo imagen → predicción → clase | `ontologia_logistica.graphml` y lectura verificada |
| Ejecución reproducible | Python 3.14 fijado en entorno y Docker en lugar de la versión ilustrativa de clase | Comando anterior y pruebas automatizadas |

La equivalencia funcional no implica rendimiento operativo: el MLP queda por debajo de la línea base. No se agrega un ejercicio SQLite paralelo para copiar el ejemplo.
