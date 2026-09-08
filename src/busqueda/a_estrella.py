# Dashboard · Semana 04 — Búsqueda y replanificación
"""Implementación del algoritmo de búsqueda heurística A* para rutas de distribución."""

# Permite usar anotaciones de tipo avanzadas y referencias hacia adelante (ej. clases no definidas aún)
from __future__ import annotations

# dataclass: decorador para estructurar clases de datos sin escribir manualmente __init__ ni __repr__
# field: función auxiliar para definir valores por defecto mutables como listas vacías (default_factory=list)
from dataclasses import dataclass, field

# heapq: biblioteca estándar de Python que implementa una cola de prioridad basada en un montículo binario (min-heap).
# Se usa para extraer siempre en O(log N) el nodo con menor costo f(n).
import heapq

# time: biblioteca estándar para medir el tiempo real de ejecución con time.perf_counter() de alta resolución
import time

# Callable: tipo de tipado que indica que un parámetro puede recibir una función invocable (como la heurística)
from typing import Callable

# GrafoEntregas: clase que modela la red vial con sus paradas y calles ponderadas
# Parada: dataclass que almacena los datos de cada parada (coordenadas latitud y longitud, id, etc.)
from src.busqueda.grafo import GrafoEntregas, Parada

# haversine_km: función matemática que calcula la distancia en línea recta en kilómetros sobre la superficie esférica de la Tierra
from src.comun.geo import haversine_km


@dataclass
class ResultadoBusqueda:
    """Resultado estructurado de un algoritmo de búsqueda de rutas.

    Define y documenta qué guarda cada variable del resultado:
    """

    # algoritmo: variable tipo str (texto) que guarda el nombre del algoritmo ejecutado (ej: "A*")
    algoritmo: str

    # inicio: variable tipo str (texto) que guarda el ID del nodo de partida (ej: "(0,0)" o "amzn_stop_01")
    inicio: str

    # meta: variable tipo str (texto) que guarda el ID del nodo de destino final (ej: "(4,4)")
    meta: str

    # encontrado: variable tipo bool (True/False) que indica si se logró encontrar un camino transitable hasta la meta
    encontrado: bool

    # ruta: variable tipo list[str] (lista de textos) que guarda la secuencia ordenada de paradas [inicio, ..., meta]
    ruta: list[str] = field(default_factory=list)

    # costo_total: variable tipo float (decimal) que guarda la suma de costos g(meta) (tiempo en segundos o distancia en km)
    # Inicia en float("inf") por si no se encuentra camino
    costo_total: float = float("inf")

    # nodos_expandidos: variable tipo int (entero) que cuenta cuántos nodos fueron extraídos de la cola con heappop
    nodos_expandidos: int = 0

    # nodos_visitados: variable tipo int (entero) que cuenta el total de nodos descubiertos e insertados en la frontera
    nodos_visitados: int = 0

    # tiempo_ms: variable tipo float (decimal) que guarda el tiempo de cómputo en milisegundos (ms)
    tiempo_ms: float = 0.0

    # explicacion: variable tipo list[dict] (lista de diccionarios) que guarda el paso a paso didáctico para el dashboard
    explicacion: list[dict] = field(default_factory=list)


# =============================================================================
# HEURÍSTICAS: "UNA BRÚJULA PARA ORIENTAR LA BÚSQUEDA" (Guía Semana 4, Sección 6)
# h(n) mira hacia adelante: estimación del costo restante desde el estado n hasta la meta.
# =============================================================================

def heuristica_haversine_segundos(
    actual: Parada,
    meta: Parada,
    v_max_kmh: float = 80.0,
) -> float:
    """Heurística geodésica admisible para matrices de tiempo de viaje en segundos.

    FÓRMULA MATEMÁTICA:
        h(n) = haversine_km(n, meta) / v_max

    TÉRMINOS DE LA ECUACIÓN:
    - haversine_km(n, meta): Distancia geodésica en línea recta sobre la esfera terrestre (km).
    - v_max: Velocidad máxima física de diseño de la flota (80 km/h = 80/3600 km/s ≈ 0.0222 km/s).
    - h(n): Estimación de tiempo mínimo teórico en segundos.

    DEMOSTRACIÓN DE ADMISIBILIDAD (Guía Semana 4, Sección 7: h(n) <= h*(n)):
    1. Distancia: Por geometría esférica, la línea recta es la distancia mínima absoluta:
          distancia_linea_recta <= distancia_vial_por_calles
    2. Velocidad: Ningún vehículo puede superar la velocidad máxima permitida:
          velocidad_real <= v_max
    3. Cociente: Al dividir el numerador mínimo por el denominador máximo:
          h(n) = dist_min / v_max <= dist_real / v_real = h*(n)
    CONCLUSION: La estimación NUNCA sobreestima el costo real (h(n) <= h*(n)).
    Por lo tanto, A* garantiza encontrar la solución ÓPTIMA de costo mínimo.

    DEMOSTRACIÓN DE CONSISTENCIA / MONOTONÍA (Desigualdad Triangular):
        h(u) <= c(u, v) + h(v)
    Para todo par de paradas adyacentes (u, v), la estimación directa desde 'u' nunca
    supera el costo de ir a 'v' más la estimación desde 'v'. Esto asegura que f(n)
    nunca decrece y ningún nodo necesita reabrirse.
    """
    # Condición de parada de la heurística: en la meta el costo restante es cero
    if actual.stop_id == meta.stop_id:
        return 0.0

    # ESTA VARIABLE dist_km (float) GUARDA: La distancia geodésica en km calculada con Haversine
    dist_km = haversine_km(actual.lat, actual.lng, meta.lat, meta.lng)

    # ESTA VARIABLE v_max_kms (float) GUARDA: La velocidad máxima convertida a km/s (80 / 3600 = 0.0222 km/s)
    # max(v_max_kmh, 1.0) es guarda defensiva contra división por cero
    v_max_kms = max(v_max_kmh, 1.0) / 3600.0

    # Retorna h(n) = distancia_km / velocidad_km_s (unidades resultantes: segundos)
    return dist_km / v_max_kms


def heuristica_haversine_km(actual: Parada, meta: Parada) -> float:
    """Heurística geodésica admisible para costos en distancia (km).

    FÓRMULA: h(n) = haversine_km(n, meta)
    Es admisible porque la distancia euclidiana en línea recta siempre es <= distancia vial.
    """
    if actual.stop_id == meta.stop_id:
        return 0.0
    return haversine_km(actual.lat, actual.lng, meta.lat, meta.lng)


def heuristica_manhattan(actual: Parada, meta: Parada) -> float:
    """Heurística Manhattan (norma L1) utilizada en la clase (Diapositiva 8 y Guía Sección 7).

    FÓRMULA MATEMÁTICA EXACTA DE LA GUÍA:
        h(a, b) = |fila_a - fila_b| + |columna_a - columna_b|

    SIGNIFICADO:
    - Cuenta cuántos pasos horizontales y verticales separan dos casillas ignorando obstáculos.
    - Es admisible y consistente en cuadrículas ortogonales (movimientos arriba, abajo, izq, der con costo 1).
    """
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
    # Medición de tiempo de cómputo para comparar contra Dijkstra/BFS
    t_inicio = time.perf_counter()

    # 1. VALIDACIÓN DE EXISTENCIA DE NODOS:
    # Verifica que los identificadores de inicio y meta existan en la red vial.
    # Si alguno no existe, retorna sin buscar (evita KeyError).
    if inicio not in grafo.nodos or meta not in grafo.nodos:
        return ResultadoBusqueda(
            algoritmo="A*",
            inicio=inicio,
            meta=meta,
            encontrado=False,
            tiempo_ms=(time.perf_counter() - t_inicio) * 1000.0,
        )

    parada_meta = grafo.nodos[meta]

    # Función auxiliar para evaluar la heurística h(n) hacia la meta elegida
    def _evaluar_h(nodo_id: str) -> float:
        if fn_heuristica is not None:
            return fn_heuristica(grafo.nodos[nodo_id], parada_meta)
        return heuristica_haversine_segundos(grafo.nodos[nodo_id], parada_meta, v_max_kmh=v_max_kmh)

    # 2. ESTRUCTURAS DE DATOS PARA LA BÚSQUEDA A*:
    # contador: entero incremental que desempata nodos con el mismo f_score en orden FIFO.
    contador = 0
    h_inicio = _evaluar_h(inicio)

    # frontier (cola de prioridad / Open Set):
    # Almacena tuplas (f_score, contador, nodo_id). heapq mantiene el min-heap.
    # PREGUNTA SUSTENTACIÓN: "¿Por qué se guarda una tupla?"
    # RESPUESTA: heapq compara primero por f_score; si hay empate compara el contador (O(1)).
    frontier: list[tuple[float, int, str]] = [(h_inicio, contador, inicio)]

    # came_from: Diccionario de punteros hacia atrás (nodo_hijo -> nodo_padre).
    # Permite reconstruir el camino óptimo desde la meta hasta el inicio al terminar.
    came_from: dict[str, str | None] = {inicio: None}

    # g_score: Almacena el menor costo real g(n) conocido desde el inicio hasta cada nodo.
    # El nodo inicial tiene costo 0.0 acumulado.
    g_score: dict[str, float] = {inicio: 0.0}

    # Contadores de auditoría y métricas de desempeño
    nodos_expandidos = 0  # Nodos extraídos de la cola con heappop
    nodos_visitados = 1   # Nodos agregados a la frontera (generados)
    explicacion = []

    # 3. CICLO PRINCIPAL DE BÚSQUEDA:
    # Se repite mientras haya nodos pendientes en la frontera
    while frontier:
        # Extrae el nodo con MENOR f(n) en tiempo O(log N).
        # PREGUNTA SUSTENTACIÓN: "¿Qué pasa si usamos lista normal y list.pop(0)?"
        # RESPUESTA: Se pierde el orden de prioridad y se convierte en BFS (FIFO).
        f_curr, _, current = heapq.heappop(frontier)
        nodos_expandidos += 1

        # TEST DE META AL EXTRAER (NO AL GENERAR):
        # PREGUNTA CLAVE: "¿Por qué verificar la meta aquí y no al generar el vecino?"
        # RESPUESTA: En A*, la meta puede generarse inicialmente con una ruta subóptima.
        # Solo al extraerla de la cola de prioridad se garantiza formalmente que ningún
        # otro camino en la frontera puede ser más corto (siempre que h sea admisible).
        if current == meta:
            break

        g_curr = g_score[current]

        # Auditoría didáctica del paso actual (usada por el dashboard)
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

        # 4. EXPANSIÓN DE SUCESORES (VECINOS ACCESIBLES):
        # grafo.vecinos() retorna solo vías transitables (excluye aristas bloqueadas).
        for nxt, costo_paso in grafo.vecinos(current):
            # Costo real tentativo para alcanzar 'nxt' pasando por 'current'
            nuevo_g = g_curr + costo_paso

            # RELAJACIÓN DE ARISTAS:
            # Se acepta el camino si 'nxt' es nuevo O si encontramos un camino más corto que el anterior.
            if nxt not in g_score or nuevo_g < g_score[nxt]:
                # Actualiza el mejor costo g(n) conocido para este vecino
                g_score[nxt] = nuevo_g

                # Calcula la heurística h(nxt) hacia la meta
                h_nxt = _evaluar_h(nxt)

                # EVALUACIÓN HEURÍSTICA: f(n) = g(n) + h(n)
                # PREGUNTA SUSTENTACIÓN: "¿Qué pasa si ponemos f_nxt = nuevo_g?"
                # RESPUESTA: Se convierte en Dijkstra (h=0, sin guía hacia la meta).
                # PREGUNTA SUSTENTACIÓN: "¿Qué pasa si ponemos f_nxt = h_nxt?"
                # RESPUESTA: Se convierte en Greedy Best-First (rápido pero sin garantía de óptimo).
                f_nxt = nuevo_g + h_nxt
                contador += 1

                # Inserción en la cola de prioridad: complejidad O(log N)
                heapq.heappush(frontier, (f_nxt, contador, nxt))

                # Registra el predecesor para poder reconstruir la ruta óptima
                came_from[nxt] = current
                nodos_visitados += 1

    # Medición final del tiempo transcurrido
    t_fin = time.perf_counter()
    tiempo_ms = (t_fin - t_inicio) * 1000.0

    # 5. VERIFICACIÓN DE SI SE ENCONTRÓ LA META:
    # Si la meta no está en came_from, la frontera se agotó sin alcanzar el destino
    # (ejemplo: destino bloqueado o desconectado en el grafo).
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

    # 6. RECONSTRUCCIÓN DEL CAMINO ÓPTIMO:
    # Retrocede desde la meta siguiendo los punteros came_from hasta llegar a None (inicio).
    ruta = []
    cur: str | None = meta
    while cur is not None:
        ruta.append(cur)
        cur = came_from[cur]

    # Invierte la lista para tener el orden natural: [inicio, nodo_1, ..., meta]
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
