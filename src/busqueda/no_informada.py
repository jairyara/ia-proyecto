# Dashboard · Semana 04 — Búsqueda y replanificación
"""Implementación de algoritmos de búsqueda no informada para línea base."""

from __future__ import annotations

# deque: estructura de cola de doble extremo para inserciones y extracciones O(1) en BFS
from collections import deque
# heapq: módulo de cola de prioridad (min-heap binario) para Dijkstra en O(log N)
import heapq
# time: cronometraje de alta precisión con time.perf_counter() en milisegundos
import time

# ResultadoBusqueda: dataclass que estructura la respuesta (ruta, costo, nodos, tiempo)
from src.busqueda.a_estrella import ResultadoBusqueda
# GrafoEntregas: grafo dirigido ponderado con lista de adyacencia de la red de entregas
from src.busqueda.grafo import GrafoEntregas


def dijkstra(
    grafo: GrafoEntregas,
    inicio: str,
    meta: str,
    registrar_explicacion: bool = False,
) -> ResultadoBusqueda:
    """Ejecuta el algoritmo de Dijkstra (Búsqueda de Costo Uniforme: A* con h(n)=0).

    CONCEPTOS DE SUSTENTACIÓN:
    1. ¿QUÉ ES DIJKSTRA EN EL MARCO DE A*?
       Es un caso especial de A* donde la función heurística es idénticamente cero: h(n) = 0.
       Por lo tanto, la función de evaluación es puramente: f(n) = g(n).
    2. OPTIMALIDAD:
       Como h(n) = 0 <= h*(n) para todo n, la heurística nula es trivialmente admisible.
       Por ende, Dijkstra GARANTIZA encontrar la ruta de costo mínimo.
    3. DESVENTAJA FRENTE A A*:
       Al no tener información sobre la dirección de la meta, explora en ondas concéntricas
       radiales en todas direcciones. Esto hace que expanda muchos más nodos que A*,
       consumiendo más memoria y tiempo de CPU en grafos grandes.
    """
    # ESTA VARIABLE GUARDA: Marca de tiempo inicial en segundos para medir duración
    t_inicio = time.perf_counter()

    # Validación de existencia de nodos de origen y destino en la red vial
    if inicio not in grafo.nodos or meta not in grafo.nodos:
        return ResultadoBusqueda(
            algoritmo="Dijkstra (No informada)",
            inicio=inicio,
            meta=meta,
            encontrado=False,
            tiempo_ms=(time.perf_counter() - t_inicio) * 1000.0,
        )

    # ESTA VARIABLE GUARDA: Desempatador monotónico para tuplas con mismo costo g(n)
    contador = 0
    # ESTA VARIABLE GUARDA: Cola de prioridad min-heap [(g_acumulado, contador, nodo_id)]
    # FÓRMULA MATEMÁTICA: f(n) = g(n) + 0.0 (heurística nula)
    frontier: list[tuple[float, int, str]] = [(0.0, contador, inicio)]
    # ESTA VARIABLE GUARDA: Diccionario {nodo: predecesor} para reconstruir la ruta
    came_from: dict[str, str | None] = {inicio: None}
    # ESTA VARIABLE GUARDA: Diccionario {nodo: costo_minimo_g} en segundos o km
    g_score: dict[str, float] = {inicio: 0.0}

    # ESTA VARIABLE GUARDA: Contador de nodos extraídos de la frontera
    nodos_expandidos = 0
    # ESTA VARIABLE GUARDA: Contador de nodos únicos insertados en la frontera
    nodos_visitados = 1
    # ESTA VARIABLE GUARDA: Lista con la traza de decisiones paso a paso
    explicacion = []

    while frontier:
        # Extrae el nodo con menor costo acumulado g(n) en O(log N)
        g_curr, _, current = heapq.heappop(frontier)
        nodos_expandidos += 1

        # Test de meta al extraer (garantiza costo mínimo en grafos ponderados)
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

        # Itera sobre los vecinos accesibles y no bloqueados de la parada actual
        for nxt, costo_paso in grafo.vecinos(current):
            # En Dijkstra solo importa el costo real acumulado: g(vecino) = g(actual) + c(actual, vecino)
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

    # Reconstrucción del camino óptimo desde la meta hacia el inicio
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
    """Ejecuta búsqueda en anchura (BFS) sobre el grafo de entregas.

    CONCEPTOS DE SUSTENTACIÓN:
    1. ESTRUCTURA: Usa una cola FIFO (First-In, First-Out) implementada con deque.
    2. LIMITACIÓN EN LOGÍSTICA:
       BFS encuentra el camino con MENOR NÚMERO DE PARADAS / ARISTAS (saltos).
       NO considera los costos reales (segundos o km). Por ejemplo, preferiría una ruta
       de 2 tramos de 60 minutos cada uno (total 120 min) sobre una ruta de 3 tramos
       de 10 minutos cada uno (total 30 min), resultando subóptima para transporte.
    """
    # ESTA VARIABLE GUARDA: Marca de tiempo de inicio en segundos para medir rendimiento
    t_inicio = time.perf_counter()

    # Validación de nodos de partida y llegada en la red vial
    if inicio not in grafo.nodos or meta not in grafo.nodos:
        return ResultadoBusqueda(
            algoritmo="BFS",
            inicio=inicio,
            meta=meta,
            encontrado=False,
            tiempo_ms=(time.perf_counter() - t_inicio) * 1000.0,
        )

    # ESTA VARIABLE GUARDA: Cola FIFO (First-In, First-Out) para explorar nivel por nivel
    # PROPIEDAD: Inserción al final y extracción al frente en tiempo O(1)
    queue: deque[str] = deque([inicio])
    # ESTA VARIABLE GUARDA: Diccionario {nodo: nodo_padre} para reconstrucción del camino
    came_from: dict[str, str | None] = {inicio: None}
    # ESTA VARIABLE GUARDA: Conjunto de nodos ya descubiertos para evitar ciclos infinitos
    visitados = {inicio}

    # ESTA VARIABLE GUARDA: Contador de nodos extraídos de la cola FIFO
    nodos_expandidos = 0

    while queue:
        # Extrae el nodo más antiguo de la cola (FIFO) en O(1)
        current = queue.popleft()
        nodos_expandidos += 1

        # Test de meta: si se alcanza la meta, BFS garantiza menor número de aristas
        if current == meta:
            break

        # Itera vecinos ignorando sus costos ponderados (solo importa la conectividad)
        for nxt, _ in grafo.vecinos(current):
            # Si el vecino no ha sido descubierto previamente:
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

    # ESTA VARIABLE GUARDA: Lista que contendrá la secuencia ordenada de paradas
    ruta = []
    # ESTA VARIABLE GUARDA: Puntero de rastreo que inicia en la meta y retrocede
    cur: str | None = meta
    while cur is not None:
        ruta.append(cur)
        cur = came_from[cur]
    # Invierte la lista para obtener el recorrido desde el depósito inicial
    ruta.reverse()

    # ESTA VARIABLE GUARDA: Costo real acumulado sumando el peso de cada arista recorrida
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
