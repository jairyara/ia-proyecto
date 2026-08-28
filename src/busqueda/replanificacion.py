"""Módulo de replanificación dinámica ante eventos imprevistos (vías bloqueadas)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

from src.busqueda.a_estrella import ResultadoBusqueda, a_estrella
from src.busqueda.grafo import GrafoEntregas, Parada


@dataclass
class ResultadoReplanificacion:
    """Resultado de un evento de replanificación ante contingencias."""

    ruta_original: list[str]
    paso_bloqueo: int
    nodo_actual: str
    meta_final: str
    arista_bloqueada: tuple[str, str]
    replanificacion_exitosa: bool
    nueva_subruta: list[str] = field(default_factory=list)
    ruta_completa_ejecutada: list[str] = field(default_factory=list)
    costo_original: float = 0.0
    costo_replanificado: float = 0.0
    nodos_expandidos: int = 0
    tiempo_ms: float = 0.0


def replanificar_ruta(
    grafo: GrafoEntregas,
    ruta_planificada: list[str],
    paso_bloqueo: int,
    arista_bloqueada: tuple[str, str] | None = None,
    fn_heuristica: Callable[[Parada, Parada], float] | None = None,
    v_max_kmh: float = 80.0,
) -> ResultadoReplanificacion:
    """Simula la ejecución de una ruta hasta encontrar una vía bloqueada y replanifica con A*.

    Args:
        grafo: El grafo vial.
        ruta_planificada: Lista ordenada de paradas planificadas.
        paso_bloqueo: Índice del nodo en la ruta donde se detecta el bloqueo al intentar avanzar.
        arista_bloqueada: Tupla (origen, destino) de la vía cerrada. Si es None, se toma (ruta[paso], ruta[paso+1]).
        fn_heuristica: Función heurística para A*.
        v_max_kmh: Velocidad máxima para la heurística Haversine.
    """
    if len(ruta_planificada) < 2 or paso_bloqueo < 0 or paso_bloqueo >= len(ruta_planificada) - 1:
        raise ValueError("Paso de bloqueo inválido para la ruta especificada.")

    nodo_actual = ruta_planificada[paso_bloqueo]
    siguiente_nodo = ruta_planificada[paso_bloqueo + 1]
    meta_final = ruta_planificada[-1]

    if arista_bloqueada is None:
        arista_bloqueada = (nodo_actual, siguiente_nodo)

    # Calcular costo original
    costo_original = 0.0
    for i in range(len(ruta_planificada) - 1):
        c = grafo.aristas.get(ruta_planificada[i], {}).get(ruta_planificada[i + 1], 0.0)
        costo_original += c

    # Costo recorrido antes del bloqueo
    costo_recorrido_previo = 0.0
    for i in range(paso_bloqueo):
        c = grafo.costo_arista(ruta_planificada[i], ruta_planificada[i + 1])
        if c is not None:
            costo_recorrido_previo += c

    # Bloquear arista
    grafo.bloquear_arista(arista_bloqueada[0], arista_bloqueada[1])

    # Replanificar desde el nodo actual hasta la meta
    res_a_estrella = a_estrella(
        grafo=grafo,
        inicio=nodo_actual,
        meta=meta_final,
        fn_heuristica=fn_heuristica,
        v_max_kmh=v_max_kmh,
    )

    if not res_a_estrella.encontrado:
        return ResultadoReplanificacion(
            ruta_original=ruta_planificada,
            paso_bloqueo=paso_bloqueo,
            nodo_actual=nodo_actual,
            meta_final=meta_final,
            arista_bloqueada=arista_bloqueada,
            replanificacion_exitosa=False,
            costo_original=costo_original,
            nodos_expandidos=res_a_estrella.nodos_expandidos,
            tiempo_ms=res_a_estrella.tiempo_ms,
        )

    # Ruta completa: recorrido hasta el bloqueo + nueva subruta desde nodo_actual
    ruta_ejecutada = list(ruta_planificada[:paso_bloqueo]) + res_a_estrella.ruta
    costo_total = costo_recorrido_previo + res_a_estrella.costo_total

    return ResultadoReplanificacion(
        ruta_original=ruta_planificada,
        paso_bloqueo=paso_bloqueo,
        nodo_actual=nodo_actual,
        meta_final=meta_final,
        arista_bloqueada=arista_bloqueada,
        replanificacion_exitosa=True,
        nueva_subruta=res_a_estrella.ruta,
        ruta_completa_ejecutada=ruta_ejecutada,
        costo_original=costo_original,
        costo_replanificado=costo_total,
        nodos_expandidos=res_a_estrella.nodos_expandidos,
        tiempo_ms=res_a_estrella.tiempo_ms,
    )
