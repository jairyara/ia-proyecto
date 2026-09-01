"""Proyección didáctica de búsqueda, sin modificar los contratos de ``src``.

La traza representa los mismos estados (frontera, cerrados y puntajes) del
algoritmo académico. El resultado canónico siempre se obtiene de ``src`` y las
pruebas comprueban que ambos recorridos conservan costo y ruta final.
"""

from __future__ import annotations

from collections import deque
from dataclasses import asdict
from functools import lru_cache
import heapq
import json
import math
from pathlib import Path
from typing import Any, Callable

from api.schemas.busqueda_dto import (
    AristaBloqueada,
    ReplanificacionRequest,
    SimulacionBusquedaRequest,
)
from api.services.contenido import fragmento_traza
from src.busqueda.a_estrella import (
    ResultadoBusqueda,
    a_estrella,
    heuristica_haversine_segundos,
    heuristica_manhattan,
)
from src.busqueda.grafo import GrafoEntregas, Parada
from src.busqueda.no_informada import bfs, dijkstra
from src.busqueda.replanificacion import replanificar_ruta


ROOT = Path(__file__).resolve().parent.parent.parent
AMAZON_DATA = ROOT / "data" / "amazon_rutas_muestra.json"
DEFAULT_GRID_OBSTACLES = {(1, 1), (1, 2), (1, 3), (2, 3), (3, 1)}
MAX_TRACE_STEPS = 720
MAX_NEIGHBORS_PER_STEP = 12


def heuristica_euclidiana(actual: Parada, meta: Parada) -> float:
    """Distancia euclidiana admisible para movimientos ortogonales unitarios."""

    return math.hypot(actual.lat - meta.lat, actual.lng - meta.lng)


@lru_cache(maxsize=1)
def cargar_datos_amazon() -> dict[str, dict[str, Any]]:
    if not AMAZON_DATA.exists():
        raise FileNotFoundError(f"No existe el dataset de rutas: {AMAZON_DATA}")
    return json.loads(AMAZON_DATA.read_text(encoding="utf-8"))


def listar_rutas_amazon() -> list[dict[str, Any]]:
    """Metadatos suficientes para configurar la simulación desde el frontend."""

    rutas = []
    for route_id, ruta in cargar_datos_amazon().items():
        paradas = [
            {
                "id": parada["stop_id"],
                "lat": float(parada.get("lat", 0.0)),
                "lng": float(parada.get("lng", 0.0)),
                "tipo": parada.get("type", "Dropoff"),
            }
            for parada in ruta.get("stops", [])
        ]
        rutas.append(
            {
                "route_id": route_id,
                "estacion": ruta.get("station_code", "—"),
                "fecha": ruta.get("date", "—"),
                "deposito": ruta.get("depot_stop_id"),
                "num_paradas": len(paradas),
                "paradas": paradas,
            }
        )
    return rutas


def _crear_grafo(
    solicitud: SimulacionBusquedaRequest,
) -> tuple[GrafoEntregas, str, str, dict[str, Any]]:
    if solicitud.entorno == "cuadricula":
        obstaculos = {(item.fila, item.columna) for item in solicitud.obstaculos}
        grid = [
            "".join("#" if (fila, col) in obstaculos else "." for col in range(5))
            for fila in range(5)
        ]
        grafo = GrafoEntregas.desde_cuadricula(grid)
        inicio = solicitud.inicio or "(0,0)"
        meta = solicitud.meta or "(4,4)"
        contexto = {"filas": 5, "columnas": 5, "obstaculos": sorted(obstaculos)}
    else:
        datos = cargar_datos_amazon()
        if solicitud.route_id not in datos:
            raise ValueError(f"Ruta Amazon desconocida: {solicitud.route_id}")
        ruta = datos[solicitud.route_id]
        grafo = GrafoEntregas.desde_amazon_ruta(ruta)
        inicio = solicitud.inicio or ruta["depot_stop_id"]
        destinos = [nodo for nodo in grafo.nodos if nodo != inicio]
        if not destinos:
            raise ValueError("La ruta Amazon no contiene un destino disponible")
        meta = solicitud.meta or destinos[min(5, len(destinos) - 1)]
        contexto = {
            "route_id": solicitud.route_id,
            "estacion": ruta.get("station_code", "—"),
            "fecha": ruta.get("date", "—"),
        }

    if inicio not in grafo.nodos:
        raise ValueError(f"El nodo inicial {inicio!r} no existe o está bloqueado")
    if meta not in grafo.nodos:
        raise ValueError(f"La meta {meta!r} no existe o está bloqueada")
    if inicio == meta:
        raise ValueError("El inicio y la meta deben ser diferentes")

    for arista in solicitud.aristas_bloqueadas:
        if arista.origen not in grafo.nodos or arista.destino not in grafo.nodos:
            raise ValueError(
                f"El tramo {arista.origen!r} → {arista.destino!r} no pertenece al grafo"
            )
        grafo.bloquear_arista(arista.origen, arista.destino)
    return grafo, inicio, meta, contexto


def _seleccionar_heuristica(
    solicitud: SimulacionBusquedaRequest,
) -> Callable[[Parada, Parada], float]:
    if solicitud.heuristica == "euclidiana":
        return heuristica_euclidiana
    if solicitud.heuristica == "haversine":
        return heuristica_haversine_segundos
    return heuristica_manhattan


def _ruta_parcial(came_from: dict[str, str | None], nodo: str) -> list[str]:
    ruta: list[str] = []
    actual: str | None = nodo
    vistos: set[str] = set()
    while actual is not None and actual not in vistos:
        vistos.add(actual)
        ruta.append(actual)
        actual = came_from.get(actual)
    ruta.reverse()
    return ruta


def _resumir_frontera(
    candidatos: list[tuple[float, float, float, str]], limite: int = 10
) -> list[dict[str, float | str]]:
    mejores: dict[str, tuple[float, float, float]] = {}
    for f_score, g_score, h_score, nodo in candidatos:
        previo = mejores.get(nodo)
        if previo is None or f_score < previo[0]:
            mejores[nodo] = (f_score, g_score, h_score)
    ordenados = sorted((f, g, h, nodo) for nodo, (f, g, h) in mejores.items())
    return [
        {"nodo": nodo, "f": round(f, 3), "g": round(g, 3), "h": round(h, 3)}
        for f, g, h, nodo in ordenados[:limite]
    ]


def _snapshot(
    pasos: list[dict[str, Any]],
    *,
    evento: str,
    actual: str,
    g_actual: float,
    h_actual: float,
    frontera: list[tuple[float, float, float, str]],
    cerrados: list[str],
    came_from: dict[str, str | None],
    vecinos: list[dict[str, Any]] | None = None,
    mensaje: str,
) -> None:
    if len(pasos) >= MAX_TRACE_STEPS:
        return
    pasos.append(
        {
            "indice": len(pasos),
            "evento": evento,
            "linea_activa": evento,
            "actual": actual,
            "g": round(g_actual, 3),
            "h": round(h_actual, 3),
            "f": round(g_actual + h_actual, 3),
            "frontera": _resumir_frontera(frontera),
            "cerrados": list(cerrados),
            "ruta_parcial": _ruta_parcial(came_from, actual),
            "vecinos": (vecinos or [])[:MAX_NEIGHBORS_PER_STEP],
            "mensaje": mensaje,
        }
    )


def _trazar_prioridad(
    grafo: GrafoEntregas,
    inicio: str,
    meta: str,
    fn_h: Callable[[Parada, Parada], float],
) -> list[dict[str, Any]]:
    """Traza A*/Dijkstra usando snapshots compactos por expansión."""

    meta_parada = grafo.nodos[meta]
    contador = 0
    h_inicio = fn_h(grafo.nodos[inicio], meta_parada)
    heap: list[tuple[float, int, str]] = [(h_inicio, contador, inicio)]
    g_score: dict[str, float] = {inicio: 0.0}
    came_from: dict[str, str | None] = {inicio: None}
    cerrados: list[str] = []
    cerrados_set: set[str] = set()
    pasos: list[dict[str, Any]] = []

    _snapshot(
        pasos,
        evento="init",
        actual=inicio,
        g_actual=0.0,
        h_actual=h_inicio,
        frontera=[(h_inicio, 0.0, h_inicio, inicio)],
        cerrados=cerrados,
        came_from=came_from,
        mensaje="Se agrega el origen a la cola de prioridad.",
    )

    while heap:
        f_actual, _, actual = heapq.heappop(heap)
        g_actual = g_score.get(actual, math.inf)
        h_actual = fn_h(grafo.nodos[actual], meta_parada)
        if f_actual > g_actual + h_actual + 1e-9 or actual in cerrados_set:
            continue
        cerrados.append(actual)
        cerrados_set.add(actual)
        frontera = [
            (
                f,
                g_score.get(nodo, math.inf),
                fn_h(grafo.nodos[nodo], meta_parada),
                nodo,
            )
            for f, _, nodo in heap
            if nodo not in cerrados_set
        ]
        _snapshot(
            pasos,
            evento="pop",
            actual=actual,
            g_actual=g_actual,
            h_actual=h_actual,
            frontera=frontera,
            cerrados=cerrados,
            came_from=came_from,
            mensaje=f"Se expande {actual}, el candidato con menor f.",
        )

        if actual == meta:
            _snapshot(
                pasos,
                evento="goal",
                actual=actual,
                g_actual=g_actual,
                h_actual=0.0,
                frontera=frontera,
                cerrados=cerrados,
                came_from=came_from,
                mensaje="La meta salió de la frontera: la búsqueda termina.",
            )
            break

        evaluados: list[dict[str, Any]] = []
        for vecino, costo in grafo.vecinos(actual):
            nuevo_g = g_actual + costo
            anterior = g_score.get(vecino, math.inf)
            mejora = nuevo_g < anterior
            h_vecino = fn_h(grafo.nodos[vecino], meta_parada)
            evaluados.append(
                {
                    "nodo": vecino,
                    "costo": round(costo, 3),
                    "nuevo_g": round(nuevo_g, 3),
                    "h": round(h_vecino, 3),
                    "f": round(nuevo_g + h_vecino, 3),
                    "mejora": mejora,
                }
            )
            if mejora:
                g_score[vecino] = nuevo_g
                came_from[vecino] = actual
                contador += 1
                heapq.heappush(heap, (nuevo_g + h_vecino, contador, vecino))

        frontera = [
            (
                f,
                g_score.get(nodo, math.inf),
                fn_h(grafo.nodos[nodo], meta_parada),
                nodo,
            )
            for f, _, nodo in heap
            if nodo not in cerrados_set
        ]
        _snapshot(
            pasos,
            evento="neighbors",
            actual=actual,
            g_actual=g_actual,
            h_actual=h_actual,
            frontera=frontera,
            cerrados=cerrados,
            came_from=came_from,
            vecinos=evaluados,
            mensaje=f"Se evaluaron {len(evaluados)} vecinos; "
            f"{sum(item['mejora'] for item in evaluados)} mejoraron su costo.",
        )
        _snapshot(
            pasos,
            evento="push",
            actual=actual,
            g_actual=g_actual,
            h_actual=h_actual,
            frontera=frontera,
            cerrados=cerrados,
            came_from=came_from,
            mensaje="La frontera queda ordenada para elegir la próxima expansión.",
        )

    return pasos


def _trazar_bfs(
    grafo: GrafoEntregas, inicio: str, meta: str
) -> list[dict[str, Any]]:
    queue: deque[str] = deque([inicio])
    came_from: dict[str, str | None] = {inicio: None}
    niveles = {inicio: 0.0}
    cerrados: list[str] = []
    pasos: list[dict[str, Any]] = []

    def frontera() -> list[tuple[float, float, float, str]]:
        return [(niveles[n], niveles[n], 0.0, n) for n in queue]

    _snapshot(
        pasos,
        evento="init",
        actual=inicio,
        g_actual=0.0,
        h_actual=0.0,
        frontera=frontera(),
        cerrados=cerrados,
        came_from=came_from,
        mensaje="BFS inicia una cola FIFO en el nivel cero.",
    )
    while queue:
        actual = queue.popleft()
        cerrados.append(actual)
        _snapshot(
            pasos,
            evento="pop",
            actual=actual,
            g_actual=niveles[actual],
            h_actual=0.0,
            frontera=frontera(),
            cerrados=cerrados,
            came_from=came_from,
            mensaje=f"BFS extrae {actual} en orden de llegada.",
        )
        if actual == meta:
            _snapshot(
                pasos,
                evento="goal",
                actual=actual,
                g_actual=niveles[actual],
                h_actual=0.0,
                frontera=frontera(),
                cerrados=cerrados,
                came_from=came_from,
                mensaje="BFS alcanzó la meta.",
            )
            break
        evaluados = []
        for vecino, costo in grafo.vecinos(actual):
            nuevo = vecino not in came_from
            evaluados.append(
                {
                    "nodo": vecino,
                    "costo": round(costo, 3),
                    "nuevo_g": niveles[actual] + 1,
                    "h": 0.0,
                    "f": niveles[actual] + 1,
                    "mejora": nuevo,
                }
            )
            if nuevo:
                came_from[vecino] = actual
                niveles[vecino] = niveles[actual] + 1
                queue.append(vecino)
        _snapshot(
            pasos,
            evento="neighbors",
            actual=actual,
            g_actual=niveles[actual],
            h_actual=0.0,
            frontera=frontera(),
            cerrados=cerrados,
            came_from=came_from,
            vecinos=evaluados,
            mensaje=f"BFS descubre {sum(item['mejora'] for item in evaluados)} nodos nuevos.",
        )
    return pasos


def _resultado_canonico(
    grafo: GrafoEntregas,
    inicio: str,
    meta: str,
    solicitud: SimulacionBusquedaRequest,
    fn_h: Callable[[Parada, Parada], float],
) -> ResultadoBusqueda:
    if solicitud.algoritmo == "dijkstra":
        return dijkstra(grafo, inicio, meta)
    if solicitud.algoritmo == "bfs":
        return bfs(grafo, inicio, meta)
    return a_estrella(grafo, inicio, meta, fn_heuristica=fn_h)


def _serializar_resultado(resultado: ResultadoBusqueda) -> dict[str, Any]:
    salida = asdict(resultado)
    if math.isinf(salida["costo_total"]):
        salida["costo_total"] = None
    salida["costo_total"] = (
        round(salida["costo_total"], 3)
        if salida["costo_total"] is not None
        else None
    )
    salida["tiempo_ms"] = round(salida["tiempo_ms"], 4)
    return salida


def _serializar_grafo(
    grafo: GrafoEntregas,
    solicitud: SimulacionBusquedaRequest,
    resultado: ResultadoBusqueda,
) -> dict[str, Any]:
    nodos = [
        {
            "id": nodo.stop_id,
            "lat": nodo.lat,
            "lng": nodo.lng,
            "tipo": nodo.tipo,
        }
        for nodo in grafo.nodos.values()
    ]
    if solicitud.entorno == "cuadricula":
        aristas = [
            {"origen": origen, "destino": destino, "costo": costo}
            for origen, destinos in grafo.aristas.items()
            for destino, costo in destinos.items()
            if origen < destino and not grafo.esta_bloqueada(origen, destino)
        ]
    else:
        aristas = []
    ruta_aristas = [
        {"origen": origen, "destino": destino}
        for origen, destino in zip(resultado.ruta, resultado.ruta[1:])
    ]
    return {"nodos": nodos, "aristas": aristas, "ruta_aristas": ruta_aristas}


def simular_busqueda(solicitud: SimulacionBusquedaRequest) -> dict[str, Any]:
    grafo, inicio, meta, contexto = _crear_grafo(solicitud)
    fn_h = _seleccionar_heuristica(solicitud)
    if solicitud.algoritmo == "dijkstra":
        fn_traza = lambda _actual, _meta: 0.0
    else:
        fn_traza = fn_h
    pasos = (
        _trazar_bfs(grafo, inicio, meta)
        if solicitud.algoritmo == "bfs"
        else _trazar_prioridad(grafo, inicio, meta, fn_traza)
    )
    resultado = _resultado_canonico(grafo, inicio, meta, solicitud, fn_h)
    referencia_a = a_estrella(grafo, inicio, meta, fn_heuristica=fn_h)
    referencia_d = dijkstra(grafo, inicio, meta)

    if resultado.encontrado:
        frontera_final: list[tuple[float, float, float, str]] = []
        pasos_antes = len(pasos)
        _snapshot(
            pasos,
            evento="path",
            actual=meta,
            g_actual=resultado.costo_total,
            h_actual=0.0,
            frontera=frontera_final,
            cerrados=pasos[-1]["cerrados"] if pasos else [],
            came_from={
                nodo: resultado.ruta[indice - 1] if indice else None
                for indice, nodo in enumerate(resultado.ruta)
            },
            mensaje="Se reconstruye la ruta óptima usando los predecesores.",
        )
        if len(pasos) > pasos_antes:
            pasos[-1]["ruta_parcial"] = resultado.ruta

    archivo_codigo, codigo = fragmento_traza(solicitud.algoritmo)
    return {
        "entorno": solicitud.entorno,
        "contexto": contexto,
        "inicio": inicio,
        "meta": meta,
        "algoritmo": solicitud.algoritmo,
        "heuristica": solicitud.heuristica,
        "archivo_codigo": archivo_codigo,
        "codigo": codigo,
        "pasos": pasos,
        "traza_truncada": len(pasos) >= MAX_TRACE_STEPS,
        "resultado": _serializar_resultado(resultado),
        "comparacion": {
            "a_estrella": _serializar_resultado(referencia_a),
            "dijkstra": _serializar_resultado(referencia_d),
        },
        "grafo": _serializar_grafo(grafo, solicitud, resultado),
        "aristas_bloqueadas": [
            {"origen": origen, "destino": destino}
            for origen, destino in sorted(grafo.aristas_bloqueadas)
        ],
    }


def replanificar_busqueda(solicitud: ReplanificacionRequest) -> dict[str, Any]:
    grafo, _, meta, _ = _crear_grafo(solicitud.simulacion)
    fn_h = _seleccionar_heuristica(solicitud.simulacion)
    origen_bloqueado = solicitud.ruta_original[solicitud.paso_bloqueo]
    destino_bloqueado = solicitud.ruta_original[solicitud.paso_bloqueo + 1]
    resultado = replanificar_ruta(
        grafo,
        solicitud.ruta_original,
        solicitud.paso_bloqueo,
        arista_bloqueada=(origen_bloqueado, destino_bloqueado),
        fn_heuristica=fn_h,
    )

    bloqueos = list(solicitud.simulacion.aristas_bloqueadas) + [
        AristaBloqueada(origen=origen_bloqueado, destino=destino_bloqueado)
    ]
    nueva_solicitud = solicitud.simulacion.model_copy(
        update={
            "inicio": resultado.nodo_actual,
            "meta": meta,
            "aristas_bloqueadas": bloqueos,
        }
    )
    simulacion = simular_busqueda(nueva_solicitud)
    replanificacion = asdict(resultado)
    for campo in ("costo_original", "costo_replanificado", "tiempo_ms"):
        if isinstance(replanificacion[campo], float) and math.isinf(
            replanificacion[campo]
        ):
            replanificacion[campo] = None
    return {"replanificacion": replanificacion, "simulacion": simulacion}
