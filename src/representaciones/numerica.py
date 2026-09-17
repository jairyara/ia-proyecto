# Dashboard · Semana 07 — Representaciones del reconocimiento
"""Representación numérica de paradas reales de Amazon Last Mile.

Cada parada se representa con un vector de tres características observadas:
distancia al depósito (km), volumen total (m³) y tiempo de servicio (s). La
referencia y la escala se calculan sobre las 14.411 filas curadas en
``data/amazon_pedidos.csv`` mediante mediana e IQR.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parent.parent.parent
DEFAULT_DATASET = ROOT / "data" / "amazon_pedidos.csv"

CAMPOS_VECTOR = (
    "distancia_deposito_km",
    "volumen_total_m3",
    "tiempo_servicio_seg",
)
UNIDADES_VECTOR = ("km", "m³", "s")
ETIQUETAS_VECTOR = (
    "Distancia al depósito",
    "Volumen total",
    "Tiempo de servicio",
)


@dataclass(frozen=True)
class VectorParada:
    """Vector numérico de una parada real del dataset Amazon."""

    distancia_deposito_km: float
    volumen_total_m3: float
    tiempo_servicio_seg: float

    def vector(self) -> np.ndarray:
        """Convierte la parada en un vector ordenado de :math:`R^3`."""
        return np.array(
            [
                self.distancia_deposito_km,
                self.volumen_total_m3,
                self.tiempo_servicio_seg,
            ],
            dtype=float,
        )


def cargar_dataset(ruta: Path = DEFAULT_DATASET) -> pd.DataFrame:
    """Carga y valida las columnas que usa Semana 07 sin imputar valores."""
    if not ruta.exists():
        raise FileNotFoundError(f"No existe el dataset Amazon: {ruta}")
    datos = pd.read_csv(ruta)
    requeridas = {"pedido_id", "route_id", "station_code", *CAMPOS_VECTOR}
    faltantes = sorted(requeridas - set(datos.columns))
    if faltantes:
        raise ValueError(f"Faltan columnas de Semana 07: {faltantes}")
    if datos[list(CAMPOS_VECTOR)].isna().any().any():
        raise ValueError("Las características numéricas contienen valores nulos")
    if datos.empty:
        raise ValueError("El dataset Amazon está vacío")
    return datos


def calcular_estadisticas(datos: pd.DataFrame) -> dict:
    """Calcula referencia, cuartiles e IQR sobre todas las observaciones."""
    matriz = datos.loc[:, list(CAMPOS_VECTOR)].astype(float)
    q1 = matriz.quantile(0.25).to_numpy(dtype=float)
    mediana = matriz.quantile(0.50).to_numpy(dtype=float)
    q3 = matriz.quantile(0.75).to_numpy(dtype=float)
    iqr = q3 - q1
    if np.any(iqr <= 0):
        raise ValueError("El IQR debe ser positivo para normalizar las variables")
    return {
        "total_registros": int(len(datos)),
        "campos": list(CAMPOS_VECTOR),
        "unidades": list(UNIDADES_VECTOR),
        "etiquetas": list(ETIQUETAS_VECTOR),
        "q1": q1.tolist(),
        "mediana": mediana.tolist(),
        "q3": q3.tolist(),
        "iqr": iqr.tolist(),
    }


def vector_desde_fila(fila: pd.Series) -> VectorParada:
    """Extrae el vector canónico de una fila validada del dataset."""
    return VectorParada(*(float(fila[campo]) for campo in CAMPOS_VECTOR))


def evaluar_vector(vector: VectorParada, estadisticas: dict) -> dict:
    """Calcula distancia euclidiana cruda y robusta respecto a la mediana."""
    muestra = vector.vector()
    referencia = np.asarray(estadisticas["mediana"], dtype=float)
    escala = np.asarray(estadisticas["iqr"], dtype=float)
    diferencia = muestra - referencia
    diferencia_normalizada = diferencia / escala
    contribuciones = np.square(diferencia_normalizada)
    return {
        "vector": muestra.tolist(),
        "referencia_mediana": referencia.tolist(),
        "escala_iqr": escala.tolist(),
        "diferencia": diferencia.tolist(),
        "diferencia_normalizada": diferencia_normalizada.tolist(),
        "contribuciones_cuadradas": contribuciones.tolist(),
        "distancia_cruda": float(np.linalg.norm(diferencia)),
        "distancia_normalizada": float(np.linalg.norm(diferencia_normalizada)),
        "campos": [
            {
                "campo": campo,
                "etiqueta": etiqueta,
                "unidad": unidad,
                "valor": float(valor),
                "referencia": float(ref),
                "diferencia": float(diff),
                "diferencia_normalizada": float(diff_norm),
                "contribucion_cuadrada": float(contribucion),
            }
            for campo, etiqueta, unidad, valor, ref, diff, diff_norm, contribucion in zip(
                CAMPOS_VECTOR,
                ETIQUETAS_VECTOR,
                UNIDADES_VECTOR,
                muestra,
                referencia,
                diferencia,
                diferencia_normalizada,
                contribuciones,
            )
        ],
    }


def perfiles_demostracion(datos: pd.DataFrame, estadisticas: dict) -> list[dict]:
    """Selecciona cinco perfiles reales mediante criterios deterministas."""
    matriz = datos.loc[:, list(CAMPOS_VECTOR)].astype(float)
    referencia = np.asarray(estadisticas["mediana"], dtype=float)
    escala = np.asarray(estadisticas["iqr"], dtype=float)
    distancias = np.linalg.norm((matriz.to_numpy() - referencia) / escala, axis=1)
    q3 = pd.Series(estadisticas["q3"], index=CAMPOS_VECTOR)
    supera_tres = matriz.gt(q3).sum(axis=1) == 3
    candidatos = [
        ("nominal", int(np.argmin(distancias)), "Más cercana a la mediana"),
        ("distancia", int(matriz["distancia_deposito_km"].idxmax()), "Mayor distancia"),
        ("volumen", int(matriz["volumen_total_m3"].idxmax()), "Mayor volumen"),
        ("servicio", int(matriz["tiempo_servicio_seg"].idxmax()), "Mayor tiempo de servicio"),
        ("triple", int(supera_tres[supera_tres].index[0]), "Supera los tres percentiles 75"),
    ]
    perfiles = []
    for codigo, indice, criterio in candidatos:
        fila = datos.loc[indice]
        perfiles.append(
            {
                "codigo": codigo,
                "criterio": criterio,
                "pedido_id": str(fila["pedido_id"]),
                "route_id": str(fila["route_id"]),
                "station_code": str(fila["station_code"]),
                "vector": vector_desde_fila(fila).vector().tolist(),
            }
        )
    return perfiles
