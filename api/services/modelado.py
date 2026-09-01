"""Carga reproducible e inferencia explicable del baseline supervisado."""

from __future__ import annotations

from functools import lru_cache
import json
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd

from api.schemas.modelado_dto import PedidoRequest
from src.modelado.riesgo_retraso import (
    DEFAULT_INPUT,
    DEFAULT_METRICS,
    DEFAULT_MODEL,
    entrenar_y_evaluar,
)


@lru_cache(maxsize=1)
def cargar_modelo_y_metricas() -> tuple[Any, dict[str, Any]]:
    """Usa el artefacto local o reconstruye el pipeline en un clon limpio."""

    if DEFAULT_MODEL.exists() and DEFAULT_METRICS.exists():
        modelo = joblib.load(DEFAULT_MODEL)
        metricas = json.loads(DEFAULT_METRICS.read_text(encoding="utf-8"))
        return modelo, metricas

    datos = pd.read_csv(DEFAULT_INPUT)
    resultados, mejor, modelo = entrenar_y_evaluar(datos)
    metricas = {
        "modelo_elegido": mejor,
        "resultados": resultados,
        "fuente": "reconstruido_deterministicamente",
    }
    return modelo, metricas


def obtener_metricas() -> dict[str, Any]:
    _, metricas = cargar_modelo_y_metricas()
    return metricas


def _nombre_legible(nombre: str) -> str:
    limpio = nombre.split("__", 1)[-1]
    reemplazos = {
        "distancia_km": "Distancia",
        "volumen_m3": "Volumen",
        "ventana_min": "Ventana horaria",
        "trafico_index": "Nivel de tráfico",
        "cadena_frio": "Cadena de frío",
        "hora_pico": "Hora pico",
        "zona_rural": "Zona rural",
        "prioridad_alta": "Prioridad alta",
        "prioridad_media": "Prioridad media",
        "prioridad_baja": "Prioridad baja",
    }
    return reemplazos.get(limpio, limpio.replace("_", " ").title())


def _explicar_prediccion(modelo: Any, fila: pd.DataFrame) -> list[dict[str, Any]]:
    """Calcula aportes locales exactos para logística y aproximados para RF."""

    preprocess = modelo.named_steps.get("preprocess")
    estimator = modelo.named_steps.get("model")
    if preprocess is None or estimator is None:
        return []
    valores = np.asarray(preprocess.transform(fila)).reshape(-1)
    nombres = list(preprocess.get_feature_names_out())

    if hasattr(estimator, "coef_"):
        aportes = valores * np.asarray(estimator.coef_[0])
    elif hasattr(estimator, "feature_importances_"):
        aportes = np.asarray(estimator.feature_importances_) * np.abs(valores)
    else:
        return []

    indices = np.argsort(np.abs(aportes))[::-1][:5]
    return [
        {
            "variable": _nombre_legible(nombres[indice]),
            "aporte": round(float(aportes[indice]), 4),
            "impacto": "aumenta" if aportes[indice] >= 0 else "reduce",
        }
        for indice in indices
        if abs(float(aportes[indice])) > 1e-9
    ]


def predecir_riesgo(pedido: PedidoRequest) -> dict[str, Any]:
    modelo, metricas = cargar_modelo_y_metricas()
    fila = pd.DataFrame([pedido.model_dump()])
    probabilidad = float(modelo.predict_proba(fila)[0][1])
    etiqueta = int(probabilidad >= 0.5)
    return {
        "probabilidad": round(probabilidad, 6),
        "etiqueta": etiqueta,
        "nivel": "alto" if etiqueta else "bajo",
        "modelo": metricas["modelo_elegido"],
        "umbral": 0.5,
        "factores": _explicar_prediccion(modelo, fila),
    }
