"""Modelado de grafos viales y topologías de entrega."""

from __future__ import annotations

# dataclass, field: utilidades para definir estructuras de datos inmutables y valores por defecto
from dataclasses import dataclass, field
# json: biblioteca estándar para leer y parsear archivos de rutas de Amazon Last Mile en JSON
import json
# Any, Callable: pistas de tipado para documentar entradas y salidas de métodos
from typing import Any, Callable


@dataclass(frozen=True)
class Parada:
    """Representa un nodo o punto de parada en la red logística de última milla.

    ESTA ESTRUCTURA GUARDA:
    - stop_id: identificador único de la parada (ej. 'D1' depósito, 'C24' cliente, '(0,0)' celda)
    - lat, lng: coordenadas GPS reales usadas para la fórmula de Haversine
    - tipo: 'Depot' (almacén central de salida) o 'Dropoff' (cliente / entrega)
    - zone_id: sector o zona geográfica de distribución
    - volumen_m3: volumen de los paquetes en m³ para restricciones de capacidad
    - num_paquetes: número de paquetes a entregar en esta ubicación
    """

    stop_id: str
    lat: float = 0.0
    lng: float = 0.0
    tipo: str = "Dropoff"  # "Dropoff" (cliente) o "Depot" (almacén)
    zone_id: str = ""
    volumen_m3: float = 0.0
    num_paquetes: int = 1


@dataclass
class GrafoEntregas:
    """Grafo dirigido ponderado que modela la red vial y paradas de entrega.

    CONCEPTOS DE IA PARA SUSTENTACIÓN:
    - Espacio de estados: Vértices V (paradas o intersecciones viales).
    - Acciones / Transición: Aristas dirigidas E con costo no negativo (tiempo en s o distancia en km).
    - ¿Por qué lista de adyacencia (dict de dicts)?: Las redes viales urbanas son grafos
      dispersos (cada nodo conecta con pocas calles vecinas, grado medio ~3-4). Una matriz
      usaría O(|V|^2) de memoria, mientras que dict[str, dict] ocupa O(|V| + |E|) y permite
      búsqueda de vecinos en O(1) por arista.
    """

    # ESTA VARIABLE GUARDA: Diccionario {stop_id: Parada} con todos los vértices del grafo
    nodos: dict[str, Parada] = field(default_factory=dict)
    # ESTA VARIABLE GUARDA: Lista de adyacencia {origen: {destino: costo_en_segundos_o_km}}
    aristas: dict[str, dict[str, float]] = field(default_factory=dict)
    # ESTA VARIABLE GUARDA: Conjunto {(u, v)} con las vías bloqueadas por incidentes u obras
    aristas_bloqueadas: set[tuple[str, str]] = field(default_factory=set)

    def agregar_nodo(self, parada: Parada) -> None:
        """Agrega o actualiza un nodo en el grafo y asegura su entrada en la lista de adyacencia."""
        self.nodos[parada.stop_id] = parada
        if parada.stop_id not in self.aristas:
            self.aristas[parada.stop_id] = {}

    def agregar_arista(self, origen: str, destino: str, costo: float) -> None:
        """Agrega o actualiza una arista dirigida entre dos paradas con su costo asociado.

        PREGUNTA SUSTENTACIÓN: "¿Es dirigido o no dirigido?"
        RESPUESTA: Es dirigido. Las calles reales tienen sentido único o costos asimétricos
        según el tráfico. Para vías bidireccionales se agregan dos aristas: (A->B) y (B->A).
        """
        if origen not in self.nodos:
            self.agregar_nodo(Parada(stop_id=origen))
        if destino not in self.nodos:
            self.agregar_nodo(Parada(stop_id=destino))
        self.aristas[origen][destino] = float(costo)

    def bloquear_arista(self, origen: str, destino: str) -> None:
        """Simula el cierre u obstrucción de una vía impidiendo el tránsito en esa dirección."""
        self.aristas_bloqueadas.add((origen, destino))

    def desbloquear_arista(self, origen: str, destino: str) -> None:
        """Restaura la transitabilidad de una vía previamente bloqueada."""
        self.aristas_bloqueadas.discard((origen, destino))

    def esta_bloqueada(self, origen: str, destino: str) -> bool:
        """Indica si la arista dirigida está actualmente en el conjunto de bloqueo (O(1))."""
        return (origen, destino) in self.aristas_bloqueadas

    def costo_arista(self, origen: str, destino: str) -> float | None:
        """Retorna el costo de la arista si existe y no está bloqueada. Si está bloqueada retorna None."""
        if self.esta_bloqueada(origen, destino):
            return None
        return self.aristas.get(origen, {}).get(destino)

    def vecinos(self, nodo_id: str) -> list[tuple[str, float]]:
        """Retorna lista de tuplas (nodo_vecino_id, costo) accesibles y no bloqueados.

        PREGUNTA SUSTENTACIÓN: "¿Cómo interactúa esto con A* o Dijkstra?"
        RESPUESTA: Los algoritmos de búsqueda solo consultan vecinos(nodo_id). Como esta
        función filtra dinámicamente las vías bloqueadas, el algoritmo encuentra rutas
        alternativas sin necesidad de modificar el código de búsqueda.
        """
        if nodo_id not in self.aristas:
            return []
        resultado = []
        for destino, costo in self.aristas[nodo_id].items():
            if not self.esta_bloqueada(nodo_id, destino):
                resultado.append((destino, costo))
        return resultado

    @classmethod
    def desde_amazon_ruta(cls, ruta_dict: dict[str, Any]) -> GrafoEntregas:
        """Construye un grafo a partir del diccionario de una ruta de Amazon Last Mile."""
        grafo = cls()
        for s in ruta_dict.get("stops", []):
            parada = Parada(
                stop_id=s["stop_id"],
                lat=float(s.get("lat", 0.0)),
                lng=float(s.get("lng", 0.0)),
                tipo=s.get("type", "Dropoff"),
                zone_id=s.get("zone_id", ""),
                volumen_m3=float(s.get("volumen_m3", 0.0)),
                num_paquetes=int(s.get("num_paquetes", 1)),
            )
            grafo.agregar_nodo(parada)

        tiempos = ruta_dict.get("travel_times_seg", {})
        for u, destinos in tiempos.items():
            for v, t_seg in destinos.items():
                if u != v:
                    grafo.agregar_arista(u, v, float(t_seg))

        return grafo

    @classmethod
    def desde_archivo_amazon(cls, ruta_json_path: str, route_id: str | None = None) -> GrafoEntregas:
        """Carga una ruta específica o la primera ruta disponible desde el JSON de Amazon."""
        with open(ruta_json_path, "r", encoding="utf-8") as f:
            datos = json.load(f)
        if route_id is None:
            route_id = list(datos.keys())[0]
        return cls.desde_amazon_ruta(datos[route_id])

    @classmethod
    def desde_cuadricula(
        cls,
        grid: list[str],
        costo_paso: float = 1.0,
        caracter_obstaculo: str = "#",
    ) -> GrafoEntregas:
        """Construye un grafo a partir de una cuadrícula de texto (ej. 5x5 de clase)."""
        grafo = cls()
        filas = len(grid)
        cols = len(grid[0]) if filas > 0 else 0

        for r in range(filas):
            for c in range(cols):
                if grid[r][c] != caracter_obstaculo:
                    nodo_id = f"({r},{c})"
                    parada = Parada(stop_id=nodo_id, lat=float(r), lng=float(c))
                    grafo.agregar_nodo(parada)

        for r in range(filas):
            for c in range(cols):
                if grid[r][c] != caracter_obstaculo:
                    u_id = f"({r},{c})"
                    for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        nr, nc = r + dr, c + dc
                        if 0 <= nr < filas and 0 <= nc < cols and grid[nr][nc] != caracter_obstaculo:
                            v_id = f"({nr},{nc})"
                            grafo.agregar_arista(u_id, v_id, costo_paso)

        return grafo
