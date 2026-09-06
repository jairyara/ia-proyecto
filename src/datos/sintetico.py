"""Generador sintético de pedidos para la tarea predictiva del Corte 1."""

from __future__ import annotations

# argparse: para configurar la cantidad de casos y la semilla aleatoria por línea de comandos
import argparse
# Path: para manipulación segura y multiplataforma de rutas de archivo
from pathlib import Path

# numpy (np): biblioteca para cálculo numérico vectorial, distribuciones y generación aleatoria
import numpy as np
# pandas (pd): biblioteca para manipular tablas estructuradas (DataFrames) y exportar a CSV
import pandas as pd


ROOT = Path(__file__).resolve().parent.parent.parent
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
    """Genera `casos` pedidos sintéticos con etiqueta de retraso probabilística.

    CONCEPTOS DE SUSTENTACIÓN:
    1. PROCESO GENERADOR DE DATOS (DGP):
       En lugar de inventar etiquetas arbitrarias, se simula un proceso logístico real
       usando un modelo lineal generalizado con enlace Logit (Regresión Logística).
    2. FÓRMULA MATEMÁTICA:
       z = beta_0 + sum(beta_i * x_i)  [Log-odds de retraso]
       P(retrasado = 1 | X) = sigma(z) = 1 / (1 + exp(-z))  [Función Sigmoide]
       Y = 1 si P >= 0.5, sino 0  [Regla de decisión de Bayes con umbral 0.5]
    3. RUIDO ESTOCÁSTICO:
       Se invierte la etiqueta en un 10% de los casos (flips) para simular eventos no
       observables (accidentes fortuitos, demoras del cliente) y evitar separabilidad trivial.
    """
    if casos < 20:
        raise ValueError("Se requieren al menos 20 casos para analizar la clase.")

    # ESTA VARIABLE GUARDA: Generador de números pseudoaleatorios controlado por semilla
    rng = np.random.default_rng(seed)
    # ESTA VARIABLE GUARDA: Identificadores únicos de pedido: 'PED-00001', 'PED-00002', ...
    pedido_id = [f"PED-{indice:05d}" for indice in range(1, casos + 1)]

    # ESTA VARIABLE GUARDA: Distancia en km con distribución triangular (mín=1, moda=6, máx=30)
    distancia_km = rng.triangular(left=1.0, mode=6.0, right=30.0, size=casos)
    # ESTA VARIABLE GUARDA: Volumen del paquete en m³ (mín=0.01, moda=0.08, máx=0.6)
    volumen_m3 = rng.triangular(left=0.01, mode=0.08, right=0.6, size=casos)
    # ESTA VARIABLE GUARDA: Categoría de servicio con probabilidades [25% alta, 50% media, 25% baja]
    prioridad = rng.choice(["alta", "media", "baja"], size=casos, p=[0.25, 0.5, 0.25])
    # ESTA VARIABLE GUARDA: Ventana horaria pactada en minutos (distribución uniforme de 30 a 240 min)
    ventana_min = rng.uniform(30.0, 240.0, size=casos).round().astype(int)
    # ESTA VARIABLE GUARDA: Indicador binario (1 si requiere refrigeración, 0 si es carga general, p=30%)
    cadena_frio = rng.binomial(1, 0.30, size=casos)
    # ESTA VARIABLE GUARDA: Indicador binario (1 si la entrega ocurre en horario de congestión, p=45%)
    hora_pico = rng.binomial(1, 0.45, size=casos)
    # ESTA VARIABLE GUARDA: Indicador binario (1 si el destino está en zona rural o periférica, p=25%)
    zona_rural = rng.binomial(1, 0.25, size=casos)
    # ESTA VARIABLE GUARDA: Índice continuo de congestión vial normalizado [0.0 = fluido, 1.0 = trancón]
    trafico_index = rng.uniform(0.0, 1.0, size=casos)

    # Indicadora numérica para prioridad alta (1.0 si alta, 0.0 si media o baja)
    prioridad_alta = (prioridad == "alta").astype(float)

    # FÓRMULA MATEMÁTICA: Combinación lineal de factores logísticos (Log-odds z)
    # beta_0 = -2.6 (tasa base negativa: la mayoría de los pedidos llega a tiempo)
    # beta_trafico = +1.6 (el tráfico vehicular eleva fuertemente el riesgo de retraso)
    # beta_pico = +1.3 (las horas pico aumentan la probabilidad de demora)
    # beta_ventana = -0.006 (una ventana de entrega más amplia reduce el riesgo de incumplimiento)
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
    # FÓRMULA MATEMÁTICA: Función Sigmoide Logística sigma(z) = 1 / (1 + exp(-z))
    # Acota el valor de log_odds en el rango de probabilidad [0.0, 1.0]
    probabilidad = 1.0 / (1.0 + np.exp(-log_odds))
    # Regla de clasificación: retrasado = 1 si P >= 0.50 (50%), de lo contrario 0
    retrasado = (probabilidad >= 0.5).astype(int)
    # Ruido estocástico del 10% para simular factores no capturados por las variables
    flips = rng.random(casos) < 0.10
    retrasado[flips] = 1 - retrasado[flips]

    # Construcción del DataFrame estructurado con todas las características de entrega
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
