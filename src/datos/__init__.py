"""Módulo de datos, generación sintética y extracción de fuentes externas."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.datos.amazon import (
        construir_grafos_muestra,
        procesar_paradas_a_dataframe,
        render_reporte_datos,
        seleccionar_rutas_estratificadas,
    )
    from src.datos.sintetico import generar_pedidos, guardar_pedidos

__all__ = [
    "generar_pedidos",
    "guardar_pedidos",
    "seleccionar_rutas_estratificadas",
    "procesar_paradas_a_dataframe",
    "construir_grafos_muestra",
    "render_reporte_datos",
]


def __getattr__(name: str):
    if name in {"generar_pedidos", "guardar_pedidos"}:
        import src.datos.sintetico as sintetico
        return getattr(sintetico, name)
    if name in {
        "seleccionar_rutas_estratificadas",
        "procesar_paradas_a_dataframe",
        "construir_grafos_muestra",
        "render_reporte_datos",
    }:
        import src.datos.amazon as amazon
        return getattr(amazon, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
