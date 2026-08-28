"""Generador sintético de pedidos para la tarea predictiva del Corte 1.

Produce `data/pedidos.csv` con distribuciones documentadas. La variable objetivo
`retrasado` sigue una regla probabilística logística interpretable, lo que permite
validar el baseline supervisado sin depender de un dataset externo.

La seed por defecto es fija para que el dataset, la partición de evaluación y las
métricas sean reproducibles. Los rangos y formas de las distribuciones (triangular,
uniforme y binominal) son plausibles para operaciones de última milla y quedan
justificados en `reports/riesgo-retraso.md`.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUTPUT = ROOT / "data" / "pedidos.csv"
DEFAULT_SEED = 20260828
DEFAULT_CASES = 800

FEATURE_COLUMNS = (
    "distancia_km",
    "volumen_m3",
    "prioridad",
    "ventana_min",
    "cadena_frio",
    "hora_pico",
    "zona_rural",
    "trafico_index",
)
TARGET_COLUMN = "retrasado"


def generar_pedidos(casos: int, seed: int = DEFAULT_SEED) -> pd.DataFrame:
    """Genera `casos` pedidos sintéticos con etiqueta de retraso probabilística."""

    if casos < 20:
        raise ValueError("Se requieren al menos 20 casos para analizar la clase.")

    rng = np.random.default_rng(seed)
    pedido_id = [f"PED-{indice:05d}" for indice in range(1, casos + 1)]

    distancia_km = rng.triangular(left=1.0, mode=6.0, right=30.0, size=casos)
    volumen_m3 = rng.triangular(left=0.01, mode=0.08, right=0.6, size=casos)
    prioridad = rng.choice(["alta", "media", "baja"], size=casos, p=[0.25, 0.5, 0.25])
    ventana_min = rng.uniform(30.0, 240.0, size=casos).round().astype(int)
    cadena_frio = rng.binomial(1, 0.30, size=casos)
    hora_pico = rng.binomial(1, 0.45, size=casos)
    zona_rural = rng.binomial(1, 0.25, size=casos)
    trafico_index = rng.uniform(0.0, 1.0, size=casos)

    prioridad_alta = (prioridad == "alta").astype(float)
    log_odds = (
        -2.6
        + 1.6 * trafico_index
        + 1.3 * hora_pico
        + 0.9 * prioridad_alta
        + 0.8 * zona_rural
        + 0.5 * cadena_frio
        + 0.03 * distancia_km
        - 0.006 * ventana_min
        + 1.5 * volumen_m3
    )
    probabilidad = 1.0 / (1.0 + np.exp(-log_odds))
    retrasado = (probabilidad >= 0.5).astype(int)
    flips = rng.random(casos) < 0.10
    retrasado[flips] = 1 - retrasado[flips]

    datos = pd.DataFrame(
        {
            "pedido_id": pedido_id,
            "distancia_km": np.round(distancia_km, 2),
            "volumen_m3": np.round(volumen_m3, 4),
            "prioridad": prioridad,
            "ventana_min": ventana_min,
            "cadena_frio": cadena_frio,
            "hora_pico": hora_pico,
            "zona_rural": zona_rural,
            "trafico_index": np.round(trafico_index, 3),
            TARGET_COLUMN: retrasado,
        }
    )
    columnas = ["pedido_id", *FEATURE_COLUMNS, TARGET_COLUMN]
    return datos[columnas]


def guardar_pedidos(datos: pd.DataFrame, destino: Path) -> Path:
    """Escribe el DataFrame en CSV UTF-8 y retorna la ruta generada."""

    destino.parent.mkdir(parents=True, exist_ok=True)
    datos.to_csv(destino, index=False)
    return destino


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Genera pedidos sintéticos con etiqueta de retraso."
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help=f"Ruta destino CSV (predeterminado: {DEFAULT_OUTPUT})",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=DEFAULT_SEED,
        help=f"Seed para reproducibilidad (predeterminado: {DEFAULT_SEED})",
    )
    parser.add_argument(
        "--cases",
        type=int,
        default=DEFAULT_CASES,
        help=f"Cantidad de pedidos (predeterminado: {DEFAULT_CASES})",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        datos = generar_pedidos(args.cases, args.seed)
        ruta = guardar_pedidos(datos, args.output)
    except ValueError as error:
        print(f"Error: {error}")
        return 2

    positivos = int(datos[TARGET_COLUMN].sum())
    print(f"Pedidos generados: {len(datos)} -> {ruta}")
    print(
        f"Clase positiva (retrasado=1): {positivos} ({positivos / len(datos):.1%})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
