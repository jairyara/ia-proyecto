"""Baseline supervisado de riesgo de retraso para el Corte 1.

Entrena LogisticRegression (baseline interpretable) y RandomForestClassifier
(comparación) sobre los datos de pedidos, evalúa accuracy, F1 y matriz de confusión
en una partición de evaluación independiente, elige el mejor modelo por F1 y
guarda los artefactos en `artifacts/` junto con un reporte Markdown.
"""

from __future__ import annotations

# argparse: para configurar argumentos y banderas desde la línea de comandos
import argparse
# json: para serializar y deserializar métricas y metadatos de evaluación en JSON
import json
# Path: para manejo robusto de rutas del sistema de archivos
from pathlib import Path

# joblib: para guardar y cargar en disco modelos y pipelines entrenados de Scikit-Learn
import joblib
# numpy (np): biblioteca para operaciones numéricas y matrices
import numpy as np
# pandas (pd): biblioteca para cargar y manipular tablas de datos (DataFrames)
import pandas as pd
# ColumnTransformer: aplica preprocesamiento diferenciado según el tipo de columna
from sklearn.compose import ColumnTransformer
# RandomForestClassifier: ensamble no lineal de 200 árboles con técnica de bagging
from sklearn.ensemble import RandomForestClassifier
# LogisticRegression: modelo probabilístico lineal supervisado interpretable
from sklearn.linear_model import LogisticRegression
# Métricas de evaluación: accuracy, matriz de confusión y F1-score
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score
# train_test_split: partición estratificada en conjunto de entrenamiento y evaluación
from sklearn.model_selection import train_test_split
# Pipeline: encapsula preprocesamiento y modelo para prevenir fuga de datos (Data Leakage)
from sklearn.pipeline import Pipeline
# OneHotEncoder: codifica categóricas en binarias; StandardScaler: estandarización z-score
from sklearn.preprocessing import OneHotEncoder, StandardScaler


ROOT = Path(__file__).resolve().parent.parent.parent
DEFAULT_INPUT = ROOT / "data" / "pedidos.csv"
DEFAULT_REPORT = ROOT / "reports" / "sem-02-riesgo-retraso.md"
DEFAULT_METRICS = ROOT / "artifacts" / "riesgo-retraso-metrics.json"
DEFAULT_MODEL = ROOT / "artifacts" / "riesgo-retraso-model.pkl"
# SEED: semilla fija para garantizar que la partición train/test sea 100% reproducible
SEED = 20260828
# TEST_SIZE: 25% de los datos se reserva exclusivamente para evaluación independiente
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
    """Carga el dataset de pedidos desde un archivo CSV validando su existencia previa."""
    if not ruta.exists():
        raise FileNotFoundError(
            f"No existe {ruta}. Genera primero con `python -m src.datos.sintetico`."
        )
    return pd.read_csv(ruta)


def construir_pipelines() -> dict[str, Pipeline]:
    """Construye los pipelines de preprocesamiento y modelos sin fuga de datos (Data Leakage).

    PREGUNTAS DE SUSTENTACIÓN:
    1. ¿QUÉ ES DATA LEAKAGE Y CÓMO LO PREVIENE EL PIPELINE?
       Si calculamos la media y desviación estándar sobre todo el dataset antes de dividirlo,
       la información de prueba contamina el entrenamiento. Al encapsular el preprocesamiento
       dentro de un Pipeline, el escalador solo calcula estadísticas en fit(X_train) y luego
       las aplica rígidamente en transform(X_test).
    2. ¿QUÉ HACE COLUMNTRAMSFORMER?
       Aplica transformaciones heterogéneas según el tipo de variable:
       - Numéricas: StandardScaler (centra en media 0 y varianza 1).
       - Binarias: passthrough (se dejan intactas en 0 y 1).
       - Categóricas: OneHotEncoder (crea columnas booleanas para cada categoría de prioridad).
    3. FÓRMULAS MATEMÁTICAS:
       - StandardScaler (z-score): z = (x - mu) / sigma
       - LogisticRegression (sigmoide): P(Y=1|X) = 1 / (1 + exp(-z))
       - Random Forest: Promedio de votos de T=200 árboles entrenados con muestras bootstrap
    """
    preprocess = ColumnTransformer(
        transformers=[
            # Estandarización z-score: z = (x - u) / s. Vital para que variables en km no dominen sobre m3
            ("num", StandardScaler(), NUMERIC_FEATURES),
            # Las binarias (0/1) no se alteran para conservar su semántica lógica
            ("bin", "passthrough", BINARY_FEATURES),
            # Codificación dummy para 'prioridad'; handle_unknown='ignore' previene fallos ante categorías nuevas
            ("cat", OneHotEncoder(handle_unknown="ignore"), CATEGORICAL_FEATURES),
        ]
    )
    return {
        # Modelo 1: Regresión Logística (baseline lineal, rápido y explicable)
        "logistic_regression": Pipeline(
            [
                ("preprocess", preprocess),
                ("model", LogisticRegression(max_iter=1000, random_state=SEED)),
            ]
        ),
        # Modelo 2: Random Forest (ensamble no lineal de 200 árboles de decisión con bagging)
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
    """Entrena los modelos candidatos, evalúa métricas en test y selecciona el mejor.

    PREGUNTAS DE SUSTENTACIÓN:
    1. ¿POR QUÉ stratify=y EN train_test_split?
       Garantiza que la proporción de entregas retrasadas (clase 1) sea exactamente la misma
       en el conjunto de entrenamiento (75%) y en el de prueba (25%), evitando sesgos de partición.
    2. ¿POR QUÉ SE ELIGE EL MEJOR POR F1-SCORE Y NO POR ACCURACY?
       En logística los retrasos son menos frecuentes que las entregas a tiempo (desbalance).
       Un modelo trivial que prediga siempre 'no retrasado' tendría un accuracy engañoso del ~80%
       pero un F1 de 0.0. F1 es la media armónica entre Precisión y Recall:
       F1 = 2 * (Precision * Recall) / (Precision + Recall)
       Donde Precision = TP / (TP + FP) y Recall = TP / (TP + FN).
    """
    features = NUMERIC_FEATURES + BINARY_FEATURES + CATEGORICAL_FEATURES
    # ESTA VARIABLE GUARDA: Matriz de características X (todas las variables de entrada del pedido)
    X = datos[features]
    # ESTA VARIABLE GUARDA: Vector objetivo y (etiqueta binaria: 1 retrasado, 0 puntual)
    y = datos[TARGET]

    # Partición 75% entrenamiento / 25% evaluación independiente con estratificación
    # ESTAS VARIABLES GUARDAN: Conjuntos disjuntos para entrenar y evaluar sin trampa
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=TEST_SIZE,
        random_state=SEED,
        stratify=y,
    )

    # ESTA VARIABLE GUARDA: Diccionario con las métricas comparativas de cada modelo
    resultados: dict[str, dict[str, float | list]] = {}
    for nombre, pipeline in construir_pipelines().items():
        # Entrena el pipeline (ajusta StandardScaler + OneHotEncoder + Modelo solo sobre X_train)
        pipeline.fit(X_train, y_train)

        # Inferencia y predicción sobre datos nunca antes vistos (X_test)
        predicciones = pipeline.predict(X_test)

        # Registro de métricas objetivas de evaluación
        resultados[nombre] = {
            # Accuracy: (TP + TN) / Total de casos evaluados
            "accuracy": float(accuracy_score(y_test, predicciones)),
            # F1-score: 2 * (Precision * Recall) / (Precision + Recall)
            "f1": float(f1_score(y_test, predicciones, zero_division=0)),
            # Matriz de confusión: [[TN, FP], [FN, TP]]
            "matriz_confusion": confusion_matrix(y_test, predicciones).tolist(),
            "n_train": int(len(y_train)),
            "n_test": int(len(y_test)),
            "tasa_positiva_test": float(y_test.mean()),
        }

    # Criterio de selección del mejor modelo: mayor F1-score en evaluación independiente
    mejor = max(resultados, key=lambda nombre: resultados[nombre]["f1"])
    mejor_pipeline = construir_pipelines()[mejor]
    # Reentrena el pipeline ganador sobre los datos de entrenamiento para guardarlo
    mejor_pipeline.fit(X_train, y_train)
    return resultados, mejor, mejor_pipeline


def render_report(
    resultados: dict[str, dict], mejor: str, fuente: str, entrada: str
) -> str:
    lineas = [
        "# Baseline supervisado — riesgo de retraso",
        "",
        "Reporte generado por `python -m src.modelado.riesgo_retraso`.",
        "",
        "## Datos",
        "",
        f"- Entrada: `{entrada}`",
        f"- Casos: {resultados[mejor]['n_train'] + resultados[mejor]['n_test']}",
        f"- Partición: {int((1 - TEST_SIZE) * 100)}% entrenamiento / "
        f"{int(TEST_SIZE * 100)}% evaluación (estratificada, seed={SEED})",
        "- Generador: distribuciones documentadas de `src/datos/sintetico.py` "
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
            "público *Amazon Last Mile Routing Challenge* (`data/amazon_pedidos.csv`) para contrastar el "
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
