"""Adaptador del clasificador simbólico con evidencia lista para la UI."""

from __future__ import annotations

from api.schemas.clasificacion_dto import RequerimientoRequest
from src.clasificacion.requerimientos import (
    CATEGORIES,
    DEFAULT_INPUT,
    classify_requirement,
    load_requirements,
)


def evaluar_requerimiento(solicitud: RequerimientoRequest) -> dict:
    resultado = classify_requirement(solicitud.descripcion)
    componentes = {categoria.name: categoria.component for categoria in CATEGORIES}
    evidencia = [
        {
            "area": area,
            "puntaje": resultado.scores[area],
            "palabras": list(resultado.matched_keywords[area]),
            "componente": componentes.get(area, "Revisión manual del requerimiento."),
        }
        for area in resultado.detected
    ]
    return {
        "principal": resultado.primary,
        "detectadas": list(resultado.detected),
        "evidencia": evidencia,
        "descripcion": solicitud.descripcion,
    }


def listar_ejemplos() -> list[dict[str, str]]:
    return [
        {
            "id": caso.identifier,
            "descripcion": caso.description,
            "area_esperada": caso.expected_area or "Sin referencia",
        }
        for caso in load_requirements(DEFAULT_INPUT)
    ]
