"""Modelado de grafos viales y topologías de entrega."""

from __future__ import annotations

from dataclasses import dataclass, field
import json
from typing import Any, Callable


@dataclass(frozen=True)
class Parada:
    """Representa un nodo o punto de parada en la red logística."""

    stop_id: str
    lat: float = 0.0
    lng: float = 0.0
    tipo: str = "Dropoff"  # "Dropoff" o "Depot"
    zone_id: str = ""
    volumen_m3: float = 0.0
    num_paquetes: int = 1


@dataclass
class GrafoEntregas:
    """Grafo dirigido ponderado que representa la red vial y paradas de entrega."""

    nodos: dict[str, Parada] = field(default_factory=dict)
    aristas: dict[str, dict[str, float]] = field(default_factory=dict)
    aristas_bloqueadas: set[tuple[str, str]] = field(default_factory=set)

    def agregar_nodo(self, parada: Parada) -> None:
        """Agrega o actualiza un nodo en el grafo."""
        self.nodos[parada.stop_id] = parada
        if parada.stop_id not in self.aristas:
            self.aristas[parada.stop_id] = {}

    def agregar_arista(self, origen: str, destino: str, costo: float) -> None:
        """Agrega o actualiza una arista dirigida entre dos paradas."""
        if origen not in self.nodos:
            self.agregar_nodo(Parada(stop_id=origen))
        if destino not in self.nodos:
            self.agregar_nodo(Parada(stop_id=destino))
        self.aristas[origen][destino] = float(costo)

    def bloquear_arista(self, origen: str, destino: str) -> None:
        """Simula el cierre u obstrucción de una vía impidiendo el tránsito."""
        self.aristas_bloqueadas.add((origen, destino))

    def desbloquear_arista(self, origen: str, destino: str) -> None:
        """Restaura la transitabilidad de una vía."""
        self.aristas_bloqueadas.discard((origen, destino))

    def esta_bloqueada(self, origen: str, destino: str) -> bool:
        """Indica si la arista está actualmente bloqueada."""
        return (origen, destino) in self.aristas_bloqueadas

    def costo_arista(self, origen: str, destino: str) -> float | None:
        """Retorna el costo de la arista si existe y no está bloqueada."""
        if self.esta_bloqueada(origen, destino):
            return None
        return self.aristas.get(origen, {}).get(destino)

    def vecinos(self, nodo_id: str) -> list[tuple[str, float]]:
        """Retorna lista de tuplas (nodo_vecino_id, costo) accesibles y no bloqueados."""
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
