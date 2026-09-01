"""DTO validados para simulación y replanificación de rutas."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, model_validator


Entorno = Literal["cuadricula", "amazon"]
Algoritmo = Literal["a_estrella", "dijkstra", "bfs"]
Heuristica = Literal["manhattan", "euclidiana", "haversine"]


class Coordenada(BaseModel):
    """Celda de una cuadrícula 5×5."""

    fila: int = Field(ge=0, lt=5)
    columna: int = Field(ge=0, lt=5)

    @property
    def nodo_id(self) -> str:
        return f"({self.fila},{self.columna})"


class AristaBloqueada(BaseModel):
    """Tramo dirigido que el algoritmo no puede recorrer."""

    origen: str = Field(min_length=1, max_length=100)
    destino: str = Field(min_length=1, max_length=100)


class SimulacionBusquedaRequest(BaseModel):
    """Parámetros comunes para cuadrícula sintética o grafo Amazon."""

    entorno: Entorno = "cuadricula"
    algoritmo: Algoritmo = "a_estrella"
    heuristica: Heuristica = "manhattan"
    inicio: str | None = Field(default=None, max_length=100)
    meta: str | None = Field(default=None, max_length=100)
    obstaculos: list[Coordenada] = Field(default_factory=list, max_length=23)
    route_id: str | None = Field(default=None, max_length=100)
    aristas_bloqueadas: list[AristaBloqueada] = Field(
        default_factory=list, max_length=100
    )

    @model_validator(mode="after")
    def validar_entorno(self) -> "SimulacionBusquedaRequest":
        if self.entorno == "amazon" and not self.route_id:
            raise ValueError("route_id es obligatorio para el entorno Amazon")
        if self.entorno == "cuadricula" and self.heuristica == "haversine":
            raise ValueError("Haversine solo aplica a coordenadas geográficas Amazon")
        return self


class ReplanificacionRequest(BaseModel):
    """Evento dinámico que bloquea el siguiente tramo de una ruta existente."""

    simulacion: SimulacionBusquedaRequest
    ruta_original: list[str] = Field(min_length=2, max_length=500)
    paso_bloqueo: int = Field(ge=0)

    @model_validator(mode="after")
    def validar_paso(self) -> "ReplanificacionRequest":
        if self.paso_bloqueo >= len(self.ruta_original) - 1:
            raise ValueError("paso_bloqueo debe señalar una arista de la ruta")
        return self
