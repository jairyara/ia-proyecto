"""Endpoints del motor de reglas simbólicas."""

from fastapi import APIRouter

from api.schemas.clasificacion_dto import RequerimientoRequest
from api.services.clasificacion import evaluar_requerimiento, listar_ejemplos


router = APIRouter(prefix="/api/clasificacion", tags=["clasificación simbólica"])


@router.get("/ejemplos")
def ejemplos() -> dict:
    return {"ejemplos": listar_ejemplos()}


@router.post("/evaluar-requerimiento")
def evaluar(solicitud: RequerimientoRequest) -> dict:
    return evaluar_requerimiento(solicitud)
