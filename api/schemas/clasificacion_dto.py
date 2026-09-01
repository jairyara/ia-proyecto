"""DTO del clasificador simbólico de requerimientos."""

from pydantic import BaseModel, Field


class RequerimientoRequest(BaseModel):
    descripcion: str = Field(min_length=3, max_length=1000)
