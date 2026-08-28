"""Módulo de utilidades comunes del sistema."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.comun.geo import haversine_km
    from src.comun.red import descargar_json

__all__ = ["haversine_km", "descargar_json"]


def __getattr__(name: str):
    if name == "haversine_km":
        from src.comun.geo import haversine_km
        return haversine_km
    if name == "descargar_json":
        from src.comun.red import descargar_json
        return descargar_json
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
