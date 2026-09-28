# Dashboard · Semana 08 — Reconocimiento, evidencia y ontología
"""Ejecuta el experimento visual de Semana 8 sin migraciones ni seeds implícitos."""

import argparse
import json
from pathlib import Path

from src.configuracion import ROOT
from src.vision.evidencia_mlp import registrar_modelo
from src.vision.modelo_mlp import entrenar_y_evaluar, guardar_resultado
from src.vision.ontologia import construir_ontologia, exportar_graphml
from src.vision.particion import preparar_piloto


ARTEFACTOS = ROOT / "artifacts/semana08"
INFORME = ROOT / "reports/sem-08-reconocimiento.md"


def generar_informe(meta: dict, aristas: int, registrado: bool) -> str:
    evaluacion = meta["evaluacion"]
    matriz = evaluacion["matriz_confusion"]
    convergencia = meta["modelo"]["convergencia_advertida"]
    return f"""# Semana 8 — Reconocimiento, evidencia y significado

**Dataset:** piloto visual auditado, 200 imágenes sintéticas `side` (100 por clase). No son fotografías de envíos Amazon.  
**Partición:** {meta['particion']['train']} entrenamiento / {meta['particion']['test']} prueba, estratificada por grupo, semilla {meta['particion']['semilla']}.  
**Entrada:** gris 16×16, 256 intensidades normalizadas a [0,1].  
**Modelo:** `MLPClassifier(hidden_layer_sizes=(64,), max_iter=400, random_state=42)`.  
**Versión:** `{meta['version']}`; SHA-256 del manifiesto `{meta['dataset_manifiesto_sha256']}`.  
**Registro PostgreSQL:** {'realizado' if registrado else 'pendiente; ejecutar con --registrar tras la migración'}.

## Evaluación reservada

| Métrica | Resultado |
|---|---:|
| Accuracy MLP | {evaluacion['accuracy']:.3f} |
| Accuracy línea base mayoritaria | {evaluacion['accuracy_baseline']:.3f} |
| F1 dañado | {evaluacion['por_clase']['danado']['f1-score']:.3f} |
| F1 intacto | {evaluacion['por_clase']['intacto']['f1-score']:.3f} |

Matriz de confusión; filas reales y columnas predichas en orden `danado`, `intacto`:

| Real / predicha | Dañado | Intacto |
|---|---:|---:|
| Dañado | {matriz[0][0]} | {matriz[0][1]} |
| Intacto | {matriz[1][0]} | {matriz[1][1]} |

**Convergencia:** {'se observó advertencia; el optimizador llegó al límite de iteraciones' if convergencia else 'sin advertencia'}.
**Interpretación:** el piloto es didáctico. Si el MLP no supera la línea base, no existe sustento para automatizar decisiones operativas. Incluso si la superase, el tamaño y origen sintético limitan la generalización.

## Evidencia y semántica

- Los originales y etiquetas siguen inmutables; `modelo_mlp_logistica.json` contiene parámetros, IDs exactos por partición, métricas y predicciones de prueba.
- `modelo_mlp_logistica.pkl` conserva el modelo entrenado; solo deben cargarse artefactos propios verificados por hash.
- La ontología logística GraphML contiene {aristas} relaciones, incluidas las de una imagen de prueba. Es un grafo semántico didáctico, no un razonador formal ni autorización automática de despacho.
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
"""


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--registrar", action="store_true", help="Persistir evidencia en PostgreSQL ya migrado")
    args = parser.parse_args(argv)
    particion = preparar_piloto()
    resultado = entrenar_y_evaluar(particion)
    meta = guardar_resultado(resultado, ARTEFACTOS)
    prediccion = meta["predicciones_test"][0]
    grafo = construir_ontologia(prediccion)
    exportar_graphml(grafo, ARTEFACTOS / "ontologia_logistica.graphml")
    if args.registrar:
        from src.persistencia.sesion import abrir_sesion, crear_motor
        motor = crear_motor()
        try:
            with abrir_sesion(motor) as sesion, sesion.begin():
                registrar_modelo(sesion, particion, meta, ARTEFACTOS / "modelo_mlp_logistica.pkl")
        finally:
            motor.dispose()
    INFORME.write_text(generar_informe(meta, grafo.number_of_edges(), args.registrar), encoding="utf-8")
    print(json.dumps({"version": meta["version"], "accuracy": meta["evaluacion"]["accuracy"],
                      "baseline": meta["evaluacion"]["accuracy_baseline"], "registrado": args.registrar},
                     ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
