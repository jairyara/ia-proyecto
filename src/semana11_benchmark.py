# Dashboard · Semana 11 — Benchmark y decisión de arquitectura
"""Compara cuatro modelos sobre riesgo heurístico en paradas Amazon.

Ejecutar desde la raíz: ``python -m src.semana11_benchmark``.
No sustituye el modelo operativo de Semana 2 ni modifica sus artefactos.
"""

from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
from time import perf_counter
import warnings

import numpy as np
import pandas as pd
import sklearn
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import HistGradientBoostingClassifier, RandomForestClassifier
from sklearn.exceptions import ConvergenceWarning
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, average_precision_score, confusion_matrix, f1_score, fbeta_score, precision_score, recall_score
from sklearn.model_selection import StratifiedGroupKFold, cross_val_predict
from sklearn.neural_network import MLPClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = ROOT / "data/amazon_pedidos.csv"
DEFAULT_CSV = ROOT / "artifacts/benchmark.csv"
DEFAULT_META = ROOT / "artifacts/semana11_benchmark.json"
SEED = 20260828
# Solo datos disponibles antes del despacho. secuencia_real es posterior y se excluye.
NUMERIC_FEATURES = [
    "distancia_deposito_km", "num_paquetes", "volumen_total_m3",
    "tiempo_servicio_seg", "duracion_ventana_min", "capacidad_vehiculo_m3",
]
BINARY_FEATURES = ["tiene_ventana_horaria"]
FEATURES = NUMERIC_FEATURES + BINARY_FEATURES
TARGET = "retrasado_estimado"  # regla, no llegada tardía observada
GROUP = "route_id"
MODEL_NAMES = ("logistic", "forest", "mlp", "hist")


def modelos() -> dict[str, Pipeline]:
    """Cada ajuste aprende el preprocesamiento solo desde su propio train."""
    def pipeline(modelo) -> Pipeline:
        preprocesamiento = ColumnTransformer([
            ("num", StandardScaler(), NUMERIC_FEATURES),
            ("bin", "passthrough", BINARY_FEATURES),
        ])
        return Pipeline([("preprocess", preprocesamiento), ("model", modelo)])

    return {
        "logistic": pipeline(LogisticRegression(max_iter=1500, random_state=SEED)),
        "forest": pipeline(RandomForestClassifier(n_estimators=250, random_state=SEED, n_jobs=1)),
        "mlp": pipeline(MLPClassifier(hidden_layer_sizes=(64,), max_iter=350, random_state=SEED)),
        "hist": pipeline(HistGradientBoostingClassifier(max_iter=150, random_state=SEED)),
    }


def _umbral_validado(y: pd.Series, probabilidades: np.ndarray) -> tuple[float, float]:
    """F2 favorece detectar retrasos; jamás consulta la prueba reservada."""
    candidatos = np.arange(0.025, 0.751, 0.025)
    puntajes = [fbeta_score(y, probabilidades >= umbral, beta=2, zero_division=0)
                for umbral in candidatos]
    mejor = int(np.argmax(puntajes))  # desempate determinista: menor umbral
    return float(candidatos[mejor]), float(puntajes[mejor])


def ejecutar(entrada: Path = DEFAULT_INPUT, csv: Path = DEFAULT_CSV,
            metadata: Path = DEFAULT_META) -> pd.DataFrame:
    origen = pd.read_csv(entrada)
    necesarias = FEATURES + [TARGET, GROUP, "tipo_parada"]
    if origen.empty or not set(necesarias).issubset(origen.columns):
        raise ValueError("El dataset está vacío o le faltan columnas obligatorias.")
    # Las estaciones no son entregas; siguen contabilizadas como exclusión auditable.
    datos = origen.loc[origen["tipo_parada"] == "Dropoff"].reset_index(drop=True)
    if datos.empty or datos[necesarias].isna().any().any():
        raise ValueError("El dataset está vacío o tiene variables/etiquetas faltantes.")
    if set(datos[TARGET].unique()) != {0, 1}:
        raise ValueError("La etiqueta heurística debe contener ambas clases 0 y 1.")
    X, y = datos[FEATURES], datos[TARGET].astype(int)
    grupos = datos[GROUP]
    # Primer pliegue fijo: cerca de 75/25 en filas y rutas enteras disjuntas.
    separador = StratifiedGroupKFold(n_splits=4, shuffle=True, random_state=SEED)
    train_idx, test_idx = next(separador.split(X, y, grupos))
    X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
    y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]
    grupos_train, grupos_test = grupos.iloc[train_idx], grupos.iloc[test_idx]
    if set(grupos_train) & set(grupos_test):
        raise AssertionError("Una ruta quedó en train y test.")
    cv = StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=SEED)
    pliegues = list(cv.split(X_train, y_train, grupos_train))
    filas, detalles = [], {}
    for nombre, modelo in modelos().items():
        with warnings.catch_warnings(record=True) as avisos:
            warnings.simplefilter("always", ConvergenceWarning)
            probabilidades_cv = cross_val_predict(
                modelo, X_train, y_train, cv=pliegues, method="predict_proba", n_jobs=1,
            )[:, 1]
            umbral, f2_cv = _umbral_validado(y_train, probabilidades_cv)
            inicio = perf_counter()
            modelo.fit(X_train, y_train)
            fit_seconds = perf_counter() - inicio
        # Predicción final y medición de inferencia del lote reservado: misma máquina y mismo lote.
        muestras_ms = []
        for _ in range(20):
            inicio = perf_counter()
            probabilidades_test = modelo.predict_proba(X_test)[:, 1]
            muestras_ms.append((perf_counter() - inicio) * 1000 / len(X_test))
        predicho = (probabilidades_test >= umbral).astype(int)
        matriz = confusion_matrix(y_test, predicho, labels=[0, 1])
        filas.append({
            "modelo": nombre,
            "accuracy": round(float(accuracy_score(y_test, predicho)), 4),
            "precision_retraso": round(float(precision_score(y_test, predicho, zero_division=0)), 4),
            "recall_retraso": round(float(recall_score(y_test, predicho, zero_division=0)), 4),
            "f1_retraso": round(float(f1_score(y_test, predicho, zero_division=0)), 4),
            "average_precision": round(float(average_precision_score(y_test, probabilidades_test)), 4),
            "falsos_negativos": int(matriz[1, 0]),
            "falsos_positivos": int(matriz[0, 1]),
            "fit_seconds": round(fit_seconds, 6),
            "infer_ms_por_pedido_p50": round(float(np.percentile(muestras_ms, 50)), 6),
            "infer_ms_por_pedido_p95": round(float(np.percentile(muestras_ms, 95)), 6),
            "umbral": round(umbral, 3),
        })
        detalles[nombre] = {
            "f2_cv": round(f2_cv, 4), "matriz_confusion": matriz.tolist(),
            "advertencias_convergencia": [str(w.message) for w in avisos
                                          if issubclass(w.category, ConvergenceWarning)],
        }
    tabla = pd.DataFrame(filas)
    if tuple(tabla.modelo) != MODEL_NAMES:
        raise AssertionError("El cuarteto de evaluación cambió inesperadamente.")
    csv.parent.mkdir(parents=True, exist_ok=True)
    metadata.parent.mkdir(parents=True, exist_ok=True)
    tabla.to_csv(csv, index=False)
    evidencia = {
        "version": 2, "origen": "Paradas Amazon Last Mile curadas; etiqueta de riesgo heurística, no retraso observado",
        "dataset": str(entrada.relative_to(ROOT)) if entrada.is_relative_to(ROOT) else str(entrada),
        "sha256_dataset": sha256(entrada.read_bytes()).hexdigest(),
        "sha256_codigo": sha256(Path(__file__).read_bytes()).hexdigest(),
        "sha256_csv": sha256(csv.read_bytes()).hexdigest(),
        "semilla": SEED, "test_size_objetivo": 0.25, "test_size_real": round(len(X_test) / len(datos), 4), "cv_folds": 5,
        "particion": "primer pliegue StratifiedGroupKFold(4), route_id disjunto",
        "n_raw": len(origen), "n_excluded_station": len(origen) - len(datos),
        "n_total": len(datos), "n_train": len(X_train), "n_test": len(X_test),
        "n_routes_train": grupos_train.nunique(), "n_routes_test": grupos_test.nunique(),
        "positivos_test": int(y_test.sum()),
        "tasa_retraso": round(float(y.mean()), 4),
        "variables": FEATURES, "target": TARGET,
        "variables_excluidas": ["pedido_id", "route_id", "stop_id", "secuencia_real", "fecha", "hora_salida_utc", "lat", "lng", "zone_id", "station_code"],
        "metrica_umbral": "F2 en probabilidades out-of-fold, 5 pliegues agrupados por route_id; rejilla 0.025–0.75",
        "metodo_tiempo": "fit final; inferencia lote test repetida 20 veces / n_test",
        "versiones": {"numpy": np.__version__, "pandas": pd.__version__, "scikit-learn": sklearn.__version__},
        "modelos": detalles,
        "advertencia": "La etiqueta Amazon es una regla heurística, parcialmente basada en secuencia_real; el benchmark no valida retrasos observados ni decisiones autónomas.",
    }
    metadata.write_text(json.dumps(evidencia, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return tabla


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--entrada", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--csv", type=Path, default=DEFAULT_CSV)
    parser.add_argument("--metadata", type=Path, default=DEFAULT_META)
    args = parser.parse_args()
    print(ejecutar(args.entrada, args.csv, args.metadata).to_string(index=False))


if __name__ == "__main__":
    main()
