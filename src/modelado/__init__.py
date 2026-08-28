"""Módulo de modelado predictivo y aprendizaje automático supervisado."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.modelado.riesgo_retraso import (
        cargar_pedidos,
        construir_pipelines,
        entrenar_y_evaluar,
        guardar_artefactos,
        render_report,
    )

__all__ = [
    "cargar_pedidos",
    "construir_pipelines",
    "entrenar_y_evaluar",
    "guardar_artefactos",
    "render_report",
]


def __getattr__(name: str):
    if name in {
        "cargar_pedidos",
        "construir_pipelines",
        "entrenar_y_evaluar",
        "guardar_artefactos",
        "render_report",
    }:
        import src.modelado.riesgo_retraso as riesgo
        return getattr(riesgo, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
