# Dashboard · Semana 04 — Búsqueda y replanificación
"""Módulo de replanificación dinámica ante eventos imprevistos (vías bloqueadas)."""

from __future__ import annotations

# dataclass, field: utilidades de Python para crear clases de datos inmutables y estructuras tipadas
from dataclasses import dataclass, field
# Callable: pista de tipado para indicar que una variable recibe una función (la heurística admisible)
from typing import Callable

# a_estrella, ResultadoBusqueda: motor de búsqueda heurística y estructura de resultados
from src.busqueda.a_estrella import ResultadoBusqueda, a_estrella
# GrafoEntregas, Parada: modelado de la red de transporte y las ubicaciones de entrega
from src.busqueda.grafo import GrafoEntregas, Parada


@dataclass
class ResultadoReplanificacion:
    """Resultado de un evento de replanificación ante contingencias viales.

    ESTA ESTRUCTURA GUARDA:
    - ruta_original: lista de paradas planificadas antes del incidente
    - paso_bloqueo: índice de la parada donde el vehículo detecta la obstrucción
    - nodo_actual: punto geográfico donde se encuentra el vehículo detenido
    - meta_final: punto de entrega al cliente que se debe alcanzar
    - arista_bloqueada: tupla (nodo_u, nodo_v) correspondiente al tramo cerrado
    - replanificacion_exitosa: booleano que indica si A* halló un camino alternativo
    - nueva_subruta: trayecto calculado por A* desde nodo_actual hasta meta_final
    - ruta_completa_ejecutada: tramo recorrido previo + nueva_subruta
    - costo_original: tiempo o distancia total de la ruta sin contingencias
    - costo_replanificado: costo real total incluyendo desvío
    - nodos_expandidos: esfuerzo computacional invertido en la replanificación
    - tiempo_ms: duración de cómputo del algoritmo en milisegundos
    """

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

    CICLO DE AGENTE INTELIGENTE (PERCIBIR -> PLANIFICAR -> ACTUAR -> REPLANIFICAR):
    1. El agente avanza por su ruta planificada hasta la posición 'paso_bloqueo'.
    2. Percibe que la vía inmediata hacia el siguiente punto está bloqueada por obras o accidente.
    3. Actualiza el modelo del entorno en el grafo marcando la arista como bloqueada.
    4. Replanifica una nueva trayectoria óptima desde su POSICIÓN ACTUAL hasta la meta final.

    PREGUNTA DE SUSTENTACIÓN:
    - "¿Por qué se replanifica desde 'nodo_actual' y no desde el inicio de la jornada?"
      RESPUESTA: Porque el vehículo es un agente físico en el mundo real. No puede
      teletransportarse al depósito inicial; debe continuar el trayecto desde donde se encuentra.
    - "¿Qué pasa si no existe ninguna vía alterna disponible (destino aislado)?"
      RESPUESTA: A* retorna encontrado=False, replanificacion_exitosa queda en False y se
      dispara el protocolo de contingencia (notificar al centro de despacho).
    """
    # Validación de límites de la ruta
    if len(ruta_planificada) < 2 or paso_bloqueo < 0 or paso_bloqueo >= len(ruta_planificada) - 1:
        raise ValueError("Paso de bloqueo inválido para la ruta especificada.")

    # 1. Estado del agente al momento del incidente:
    # ESTA VARIABLE GUARDA: Identificador del nodo donde la furgoneta se encuentra detenida
    nodo_actual = ruta_planificada[paso_bloqueo]
    # ESTA VARIABLE GUARDA: Siguiente parada planificada que ahora resulta inaccesible
    siguiente_nodo = ruta_planificada[paso_bloqueo + 1]
    # ESTA VARIABLE GUARDA: Nodo destino final (cliente donde se debe entregar el paquete)
    meta_final = ruta_planificada[-1]

    # ESTA VARIABLE GUARDA: Tramo vial afectado (origen, destino) que se cerrará en el grafo
    if arista_bloqueada is None:
        arista_bloqueada = (nodo_actual, siguiente_nodo)

    # 2. Costo total de la ruta original sin contingencias:
    # ESTA VARIABLE GUARDA: Suma de costos de cada arista en condiciones normales de operación
    costo_original = 0.0
    for i in range(len(ruta_planificada) - 1):
        c = grafo.aristas.get(ruta_planificada[i], {}).get(ruta_planificada[i + 1], 0.0)
        costo_original += c

    # 3. Costo real ya consumido por el vehículo antes de toparse con el bloqueo:
    # ESTA VARIABLE GUARDA: Tiempo o distancia invertida hasta llegar a nodo_actual
    costo_recorrido_previo = 0.0
    for i in range(paso_bloqueo):
        c = grafo.costo_arista(ruta_planificada[i], ruta_planificada[i + 1])
        if c is not None:
            costo_recorrido_previo += c

    # 4. Actualización del entorno: bloquear la vía en el grafo vial
    grafo.bloquear_arista(arista_bloqueada[0], arista_bloqueada[1])

    # 5. Ejecución de A* desde el estado actual (nodo_actual) hacia la meta final
    # ESTA VARIABLE GUARDA: Resultado del algoritmo A* con la nueva subruta calculada
    res_a_estrella = a_estrella(
        grafo=grafo,
        inicio=nodo_actual,
        meta=meta_final,
        fn_heuristica=fn_heuristica,
        v_max_kmh=v_max_kmh,
    )

    # Si no existe ningún camino alternativo disponible:
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

    # 6. Consolidación de la ruta real ejecutada:
    # ESTA VARIABLE GUARDA: Secuencia total recorrida (tramo previo + nueva subruta A*)
    ruta_ejecutada = list(ruta_planificada[:paso_bloqueo]) + res_a_estrella.ruta
    # ESTA VARIABLE GUARDA: Costo total combinado (costo previo consumido + costo de la subruta)
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
