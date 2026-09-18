"""Adaptador didáctico para las representaciones de Semana 07."""

from __future__ import annotations

from functools import lru_cache

from api.schemas.representaciones_dto import EvaluacionRepresentacionRequest
from src.representaciones.reconocimiento import contexto_dataset, evaluar_parada, evaluaciones_pod


@lru_cache(maxsize=1)
def obtener_contexto() -> dict:
    """Expone estadísticas Amazon y escenarios POD adaptados al proyecto."""
    return {
        "amazon": contexto_dataset(),
        "automata_pod": {
            "origen": "escenario controlado; Amazon no registra eventos A/V/F/C",
            "alfabeto": {"A": "Arribo", "V": "Validación", "F": "Firma POD", "C": "Cancelación"},
            "secuencias": evaluaciones_pod(),
        },
    }


def evaluar_representacion(solicitud: EvaluacionRepresentacionRequest) -> dict:
    """Evalúa la parada seleccionada y la secuencia POD indicada."""
    return evaluar_parada(solicitud.pedido_id, solicitud.secuencia_pod)
