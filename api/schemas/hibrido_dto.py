"""DTO del sistema híbrido de trazabilidad (Semana 5)."""

from pydantic import BaseModel, Field


class ConsultaHibridaRequest(BaseModel):
    consulta: str = Field(min_length=3, max_length=1000)
