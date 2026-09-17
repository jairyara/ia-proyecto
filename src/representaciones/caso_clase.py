# Dashboard · Semana 07 — Representaciones del reconocimiento
"""Caso base exacto proporcionado por la presentación oficial de Semana 07."""

from __future__ import annotations

import numpy as np


TRANSICIONES_01 = {
    ("q0", "0"): "q1", ("q0", "1"): "q0",
    ("q1", "0"): "q1", ("q1", "1"): "q2",
    ("q2", "0"): "q1", ("q2", "1"): "q0",
}


def trazar_01(texto: str) -> dict:
    """Recorre el AFD oficial que acepta cadenas binarias terminadas en ``01``."""
    estado = "q0"
    traza = []
    for paso, simbolo in enumerate(texto, start=1):
        destino = TRANSICIONES_01.get((estado, simbolo), "q_error")
        traza.append({"paso": paso, "simbolo": simbolo, "estado_origen": estado, "estado_destino": destino, "transicion_legal": destino != "q_error"})
        estado = destino
    return {"secuencia": texto, "estado_inicial": "q0", "estado_final": estado, "aceptada": estado == "q2", "traza": traza}


def accepts_01(texto: str) -> bool:
    """Devuelve ``True`` únicamente si la cadena termina en ``01``."""
    return trazar_01(texto)["aceptada"]


def ejecutar_caso_clase() -> dict:
    """Reproduce sin cambios conceptuales los tres bloques de la guía."""
    muestra = np.array([72.0, 0.85, 3.0])
    referencia = np.array([70.0, 0.80, 2.0])
    distancia = float(np.linalg.norm(muestra - referencia))
    hechos = {"temperatura_alta", "carga_alta", "errores_presentes"}
    conclusion = "riesgo_termico" if {"temperatura_alta", "carga_alta"}.issubset(hechos) else None
    secuencias = [trazar_01(item) for item in ("1101", "1110", "0001")]
    return {
        "origen": "Semana_07_Representaciones_del_reconocimiento_Clase.pptx",
        "numerica": {"muestra": muestra.tolist(), "referencia": referencia.tolist(), "diferencia": (muestra - referencia).tolist(), "distancia_euclidiana": distancia},
        "simbolica": {"hechos": sorted(hechos), "premisas": ["temperatura_alta", "carga_alta"], "conclusion": conclusion},
        "automata": {"alfabeto": ["0", "1"], "estados": ["q0", "q1", "q2", "q_error"], "estado_inicial": "q0", "estados_aceptacion": ["q2"], "secuencias": secuencias},
    }
