"""Baseline supervisado de riesgo de retraso para el Corte 1.

Entrena LogisticRegression (baseline interpretable) y RandomForestClassifier
(comparación) sobre `data/pedidos.csv`, evalúa accuracy, F1 y matriz de confusión
en una partición de evaluación independiente, elige el mejor modelo por F1 y
guarda los artefactos en `artifacts/` junto con un reporte Markdown.

La transformación se ajusta únicamente con entrenamiento para evitar fuga de
datos. El criterio de selección y la partición quedan documentados para mantener
las comparaciones auditables.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


ROOT = Path(__file__).resolve().parent.parent
DEFAULT_INPUT = ROOT / "data" / "pedidos.csv"
DEFAULT_REPORT = ROOT / "reports" / "riesgo-retraso.md"
DEFAULT_METRICS = ROOT / "artifacts" / "riesgo-retraso-metrics.json"
DEFAULT_MODEL = ROOT / "artifacts" / "riesgo-retraso-model.pkl"
SEED = 20260828
TEST_SIZE = 0.25

NUMERIC_FEATURES = [
    "distancia_km",
    "volumen_m3",
    "ventana_min",
    "trafico_index",
]
BINARY_FEATURES = ["cadena_frio", "hora_pico", "zona_rural"]
CATEGORICAL_FEATURES = ["prioridad"]
TARGET = "retrasado"


def cargar_pedidos(ruta: Path) -> pd.DataFrame:
    if not ruta.exists():
        raise FileNotFoundError(
            f"No existe {ruta}. Genera primero con `python -m src.generador_pedidos`."
        )
    return pd.read_csv(ruta)


def construir_pipelines() -> dict[str, Pipeline]:
    preprocess = ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), NUMERIC_FEATURES),
            ("bin", "passthrough", BINARY_FEATURES),
            ("cat", OneHotEncoder(handle_unknown="ignore"), CATEGORICAL_FEATURES),
        ]
    )
    return {
        "logistic_regression": Pipeline(
            [
                ("preprocess", preprocess),
                ("model", LogisticRegression(max_iter=1000, random_state=SEED)),
            ]
        ),
        "random_forest": Pipeline(
            [
                ("preprocess", preprocess),
                (
                    "model",
                    RandomForestClassifier(
                        n_estimators=200, random_state=SEED, n_jobs=-1
                    ),
                ),
            ]
        ),
    }


def entrenar_y_evaluar(
    datos: pd.DataFrame,
) -> tuple[dict[str, dict[str, float | list]], str, Pipeline]:
    features = NUMERIC_FEATURES + BINARY_FEATURES + CATEGORICAL_FEATURES
    X = datos[features]
    y = datos[TARGET]

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=TEST_SIZE,
        random_state=SEED,
        stratify=y,
    )

    resultados: dict[str, dict[str, float | list]] = {}
    for nombre, pipeline in construir_pipelines().items():
        pipeline.fit(X_train, y_train)
        predicciones = pipeline.predict(X_test)
        resultados[nombre] = {
            "accuracy": float(accuracy_score(y_test, predicciones)),
            "f1": float(f1_score(y_test, predicciones, zero_division=0)),
            "matriz_confusion": confusion_matrix(y_test, predicciones).tolist(),
            "n_train": int(len(y_train)),
            "n_test": int(len(y_test)),
            "tasa_positiva_test": float(y_test.mean()),
        }

    mejor = max(resultados, key=lambda nombre: resultados[nombre]["f1"])
    mejor_pipeline = construir_pipelines()[mejor]
    mejor_pipeline.fit(X_train, y_train)
    return resultados, mejor, mejor_pipeline


def render_report(
    resultados: dict[str, dict], mejor: str, fuente: str, entrada: str
) -> str:
    lineas = [
        "# Baseline supervisado — riesgo de retraso",
        "",
        "Reporte generado por `python -m src.modelo_riesgo`.",
        "",
        "## Datos",
        "",
        f"- Entrada: `{entrada}`",
        f"- Casos: {resultados[mejor]['n_train'] + resultados[mejor]['n_test']}",
        f"- Partición: {int((1 - TEST_SIZE) * 100)}% entrenamiento / "
        f"{int(TEST_SIZE * 100)}% evaluación (estratificada, seed={SEED})",
        "- Generador: distribuciones documentadas de `src/generador_pedidos.py` "
        "(triangular para distancia/volumen, uniforme para ventanas e índice de "
        "tráfico, elección ponderada para prioridad y binomial para indicadores).",
        f"- Tasa positiva en evaluación: {resultados[mejor]['tasa_positiva_test']:.3f}",
        "",
        "## Modelos comparados",
        "",
        "| Modelo | Accuracy (test) | F1 (test) |",
        "|---|---:|---:|",
    ]
    for nombre, metricas in resultados.items():
        lineas.append(
            f"| `{nombre}` | {metricas['accuracy']:.4f} | {metricas['f1']:.4f} |"
        )
    lineas.extend(
        [
            "",
            f"**Modelo elegido:** `{mejor}` (mayor F1 en evaluación).",
            "",
            "## Matriz de confusión del modelo elegido",
            "",
        ]
    )
    matriz = resultados[mejor]["matriz_confusion"]
    lineas.extend(
        [
            "| | Predicho 0 | Predicho 1 |",
            "|---|---:|---:|",
            f"| **Real 0** | {matriz[0][0]} | {matriz[0][1]} |",
            f"| **Real 1** | {matriz[1][0]} | {matriz[1][1]} |",
            "",
            "## Limitaciones",
            "",
            "- Dataset sintético: las conclusiones aplican al generador, no al dominio.",
            "- La partición fija controla comparabilidad; si se regenera el dataset "
            "cambian las métricas.",
            "- El reporte documenta el criterio de selección (F1) sin garantizar el "
            "mejor modelo absoluto.",
            "",
            "## Siguiente paso",
            "",
            "- Evaluar en el seguimiento post-Corte 1 si se integra el dataset "
            "público *Amazon Last Mile Routing Challenge* para contrastar el "
            "generador con datos reales.",
            "",
        ]
    )
    return "\n".join(lineas)


def guardar_artefactos(
    model: Pipeline,
    resultados: dict,
    mejor: str,
    ruta_metricas: Path,
    ruta_modelo: Path,
) -> None:
    ruta_metricas.parent.mkdir(parents=True, exist_ok=True)
    ruta_modelo.parent.mkdir(parents=True, exist_ok=True)

    joblib.dump(model, ruta_modelo)
    salida = {"modelo_elegido": mejor, "resultados": resultados, "seed": SEED}
    ruta_metricas.write_text(json.dumps(salida, indent=2), encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Entrena el baseline supervisado de riesgo de retraso."
    )
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output-report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--output-metrics", type=Path, default=DEFAULT_METRICS)
    parser.add_argument("--output-model", type=Path, default=DEFAULT_MODEL)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        datos = cargar_pedidos(args.input)
        resultados, mejor, modelo = entrenar_y_evaluar(datos)
        reporte = render_report(resultados, mejor, str(args.input), args.input.name)
        args.output_report.parent.mkdir(parents=True, exist_ok=True)
        args.output_report.write_text(reporte, encoding="utf-8")
        guardar_artefactos(modelo, resultados, mejor, args.output_metrics, args.output_model)
    except (FileNotFoundError, ValueError) as error:
        print(f"Error: {error}")
        return 2

    print(f"Modelo elegido: {mejor}")
    print(f"Accuracy test: {resultados[mejor]['accuracy']:.4f} | F1 test: {resultados[mejor]['f1']:.4f}")
    print(f"Reporte: {args.output_report}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
