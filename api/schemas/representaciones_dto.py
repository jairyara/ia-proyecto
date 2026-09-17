"""Contratos API para el laboratorio de representaciones de Semana 07."""

from pydantic import BaseModel, Field


class EvaluacionRepresentacionRequest(BaseModel):
    pedido_id: str = Field(min_length=9, max_length=20, pattern=r"^AMZ-\d{5}$")
    secuencia_pod: str = Field(default="AVF", max_length=12, pattern=r"^[AVFC]*$")
