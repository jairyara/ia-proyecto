"""Implementación del algoritmo de búsqueda heurística A* para rutas de distribución."""

from __future__ import annotations

from dataclasses import dataclass, field
import heapq
import time
from typing import Callable

from src.busqueda.grafo import GrafoEntregas, Parada
from src.comun.geo import haversine_km


@dataclass
class ResultadoBusqueda:
    """Resultado estructurado de un algoritmo de búsqueda de rutas."""

    algoritmo: str
    inicio: str
    meta: str
    encontrado: bool
    ruta: list[str] = field(default_factory=list)
    costo_total: float = float("inf")
    nodos_expandidos: int = 0
    nodos_visitados: int = 0
    tiempo_ms: float = 0.0
    explicacion: list[dict] = field(default_factory=list)


def heuristica_haversine_segundos(
    actual: Parada,
    meta: Parada,
    v_max_kmh: float = 80.0,
) -> float:
    """Heurística geodésica admisible para matrices de tiempo de viaje.

    Calcula la distancia Haversine en línea recta y la divide por la velocidad
    máxima estimada de la flota en km/s para obtener un límite inferior del
    tiempo de viaje en segundos (h(n) <= h*(n)).
    """
    if actual.stop_id == meta.stop_id:
        return 0.0
    dist_km = haversine_km(actual.lat, actual.lng, meta.lat, meta.lng)
    v_max_kms = max(v_max_kmh, 1.0) / 3600.0
    return dist_km / v_max_kms


def heuristica_haversine_km(actual: Parada, meta: Parada) -> float:
    """Heurística geodésica admisible para costos en distancia (km)."""
    if actual.stop_id == meta.stop_id:
        return 0.0
    return haversine_km(actual.lat, actual.lng, meta.lat, meta.lng)


def heuristica_manhattan(actual: Parada, meta: Parada) -> float:
    """Heurística Manhattan para cuadrículas sintéticas de simulación."""
    return abs(actual.lat - meta.lat) + abs(actual.lng - meta.lng)


def a_estrella(
    grafo: GrafoEntregas,
    inicio: str,
    meta: str,
    fn_heuristica: Callable[[Parada, Parada], float] | None = None,
    v_max_kmh: float = 80.0,
    registrar_explicacion: bool = False,
) -> ResultadoBusqueda:
    """Ejecuta el algoritmo de búsqueda A* sobre el grafo de entregas.

    Combina el costo acumulado real g(n) con la estimación heurística h(n)
    mediante la función f(n) = g(n) + h(n) en una cola de prioridad.
    """
    t_inicio = time.perf_counter()

    if inicio not in grafo.nodos or meta not in grafo.nodos:
        return ResultadoBusqueda(
            algoritmo="A*",
            inicio=inicio,
            meta=meta,
            encontrado=False,
            tiempo_ms=(time.perf_counter() - t_inicio) * 1000.0,
        )

    parada_meta = grafo.nodos[meta]

    def _evaluar_h(nodo_id: str) -> float:
        if fn_heuristica is not None:
            return fn_heuristica(grafo.nodos[nodo_id], parada_meta)
        return heuristica_haversine_segundos(grafo.nodos[nodo_id], parada_meta, v_max_kmh=v_max_kmh)

    # Cola de prioridad: (f_score, tiebreaker_counter, nodo_id)
    contador = 0
    h_inicio = _evaluar_h(inicio)
    frontier: list[tuple[float, int, str]] = [(h_inicio, contador, inicio)]
    came_from: dict[str, str | None] = {inicio: None}
    g_score: dict[str, float] = {inicio: 0.0}

    nodos_expandidos = 0
    nodos_visitados = 1
    explicacion = []

    while frontier:
        f_curr, _, current = heapq.heappop(frontier)
        nodos_expandidos += 1

        if current == meta:
            break

        g_curr = g_score[current]

        if registrar_explicacion:
            explicacion.append(
                {
                    "nodo": current,
                    "g": g_curr,
                    "h": f_curr - g_curr,
                    "f": f_curr,
                    "vecinos": len(grafo.vecinos(current)),
                }
            )

        for nxt, costo_paso in grafo.vecinos(current):
            nuevo_g = g_curr + costo_paso
            if nxt not in g_score or nuevo_g < g_score[nxt]:
                g_score[nxt] = nuevo_g
                h_nxt = _evaluar_h(nxt)
                f_nxt = nuevo_g + h_nxt
                contador += 1
                heapq.heappush(frontier, (f_nxt, contador, nxt))
                came_from[nxt] = current
                nodos_visitados += 1

    t_fin = time.perf_counter()
    tiempo_ms = (t_fin - t_inicio) * 1000.0

    if meta not in came_from:
        return ResultadoBusqueda(
            algoritmo="A*",
            inicio=inicio,
            meta=meta,
            encontrado=False,
            nodos_expandidos=nodos_expandidos,
            nodos_visitados=nodos_visitados,
            tiempo_ms=tiempo_ms,
            explicacion=explicacion,
        )

    # Reconstruir camino
    ruta = []
    cur: str | None = meta
    while cur is not None:
        ruta.append(cur)
        cur = came_from[cur]
    ruta.reverse()

    return ResultadoBusqueda(
        algoritmo="A*",
        inicio=inicio,
        meta=meta,
        encontrado=True,
        ruta=ruta,
        costo_total=g_score[meta],
        nodos_expandidos=nodos_expandidos,
        nodos_visitados=nodos_visitados,
        tiempo_ms=tiempo_ms,
        explicacion=explicacion,
    )
