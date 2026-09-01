"""DTO del baseline supervisado de riesgo de retraso."""

from typing import Literal

from pydantic import BaseModel, Field


class PedidoRequest(BaseModel):
    distancia_km: float = Field(ge=1.0, le=30.0)
    volumen_m3: float = Field(ge=0.01, le=0.6)
    prioridad: Literal["alta", "media", "baja"] = "media"
    ventana_min: int = Field(ge=30, le=240)
    cadena_frio: int = Field(ge=0, le=1)
    hora_pico: int = Field(ge=0, le=1)
    zona_rural: int = Field(ge=0, le=1)
    trafico_index: float = Field(ge=0.0, le=1.0)
