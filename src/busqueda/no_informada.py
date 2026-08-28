"""Implementación de algoritmos de búsqueda no informada para línea base."""

from __future__ import annotations

from collections import deque
import heapq
import time

from src.busqueda.a_estrella import ResultadoBusqueda
from src.busqueda.grafo import GrafoEntregas


def dijkstra(
    grafo: GrafoEntregas,
    inicio: str,
    meta: str,
    registrar_explicacion: bool = False,
) -> ResultadoBusqueda:
    """Ejecuta el algoritmo de Dijkstra (Búsqueda de Costo Uniforme: A* con h(n)=0).

    Sirve como línea base cuantitativa para evaluar el impacto de la heurística.
    """
    t_inicio = time.perf_counter()

    if inicio not in grafo.nodos or meta not in grafo.nodos:
        return ResultadoBusqueda(
            algoritmo="Dijkstra (No informada)",
            inicio=inicio,
            meta=meta,
            encontrado=False,
            tiempo_ms=(time.perf_counter() - t_inicio) * 1000.0,
        )

    contador = 0
    frontier: list[tuple[float, int, str]] = [(0.0, contador, inicio)]
    came_from: dict[str, str | None] = {inicio: None}
    g_score: dict[str, float] = {inicio: 0.0}

    nodos_expandidos = 0
    nodos_visitados = 1
    explicacion = []

    while frontier:
        g_curr, _, current = heapq.heappop(frontier)
        nodos_expandidos += 1

        if current == meta:
            break

        if registrar_explicacion:
            explicacion.append(
                {
                    "nodo": current,
                    "g": g_curr,
                    "h": 0.0,
                    "f": g_curr,
                    "vecinos": len(grafo.vecinos(current)),
                }
            )

        for nxt, costo_paso in grafo.vecinos(current):
            nuevo_g = g_curr + costo_paso
            if nxt not in g_score or nuevo_g < g_score[nxt]:
                g_score[nxt] = nuevo_g
                contador += 1
                heapq.heappush(frontier, (nuevo_g, contador, nxt))
                came_from[nxt] = current
                nodos_visitados += 1

    t_fin = time.perf_counter()
    tiempo_ms = (t_fin - t_inicio) * 1000.0

    if meta not in came_from:
        return ResultadoBusqueda(
            algoritmo="Dijkstra (No informada)",
            inicio=inicio,
            meta=meta,
            encontrado=False,
            nodos_expandidos=nodos_expandidos,
            nodos_visitados=nodos_visitados,
            tiempo_ms=tiempo_ms,
            explicacion=explicacion,
        )

    ruta = []
    cur: str | None = meta
    while cur is not None:
        ruta.append(cur)
        cur = came_from[cur]
    ruta.reverse()

    return ResultadoBusqueda(
        algoritmo="Dijkstra (No informada)",
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


def bfs(
    grafo: GrafoEntregas,
    inicio: str,
    meta: str,
) -> ResultadoBusqueda:
    """Ejecuta búsqueda en anchura (BFS) sobre el grafo de entregas."""
    t_inicio = time.perf_counter()

    if inicio not in grafo.nodos or meta not in grafo.nodos:
        return ResultadoBusqueda(
            algoritmo="BFS",
            inicio=inicio,
            meta=meta,
            encontrado=False,
            tiempo_ms=(time.perf_counter() - t_inicio) * 1000.0,
        )

    queue: deque[str] = deque([inicio])
    came_from: dict[str, str | None] = {inicio: None}
    visitados = {inicio}

    nodos_expandidos = 0

    while queue:
        current = queue.popleft()
        nodos_expandidos += 1

        if current == meta:
            break

        for nxt, _ in grafo.vecinos(current):
            if nxt not in visitados:
                visitados.add(nxt)
                came_from[nxt] = current
                queue.append(nxt)

    t_fin = time.perf_counter()
    tiempo_ms = (t_fin - t_inicio) * 1000.0

    if meta not in came_from:
        return ResultadoBusqueda(
            algoritmo="BFS",
            inicio=inicio,
            meta=meta,
            encontrado=False,
            nodos_expandidos=nodos_expandidos,
            nodos_visitados=len(visitados),
            tiempo_ms=tiempo_ms,
        )

    ruta = []
    cur: str | None = meta
    while cur is not None:
        ruta.append(cur)
        cur = came_from[cur]
    ruta.reverse()

    # Calcular costo real acumulado del camino
    costo_total = 0.0
    for i in range(len(ruta) - 1):
        c = grafo.costo_arista(ruta[i], ruta[i + 1])
        if c is not None:
            costo_total += c

    return ResultadoBusqueda(
        algoritmo="BFS",
        inicio=inicio,
        meta=meta,
        encontrado=True,
        ruta=ruta,
        costo_total=costo_total,
        nodos_expandidos=nodos_expandidos,
        nodos_visitados=len(visitados),
        tiempo_ms=tiempo_ms,
    )
