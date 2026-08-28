"""Subpaquete de búsqueda heurística, optimización y replanificación de rutas."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.busqueda.a_estrella import (
        ResultadoBusqueda,
        a_estrella,
        heuristica_haversine_km,
        heuristica_haversine_segundos,
        heuristica_manhattan,
    )
    from src.busqueda.grafo import GrafoEntregas, Parada
    from src.busqueda.no_informada import bfs, dijkstra
    from src.busqueda.replanificacion import ResultadoReplanificacion, replanificar_ruta

__all__ = [
    "GrafoEntregas",
    "Parada",
    "ResultadoBusqueda",
    "a_estrella",
    "heuristica_haversine_km",
    "heuristica_haversine_segundos",
    "heuristica_manhattan",
    "dijkstra",
    "bfs",
    "ResultadoReplanificacion",
    "replanificar_ruta",
]


def __getattr__(name: str):
    if name in ("GrafoEntregas", "Parada"):
        from src.busqueda import grafo
        return getattr(grafo, name)
    if name in (
        "ResultadoBusqueda",
        "a_estrella",
        "heuristica_haversine_km",
        "heuristica_haversine_segundos",
        "heuristica_manhattan",
    ):
        from src.busqueda import a_estrella
        return getattr(a_estrella, name)
    if name in ("dijkstra", "bfs"):
        from src.busqueda import no_informada
        return getattr(no_informada, name)
    if name in ("ResultadoReplanificacion", "replanificar_ruta"):
        from src.busqueda import replanificacion
        return getattr(replanificacion, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
