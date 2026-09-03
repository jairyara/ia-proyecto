"""Endpoints del sistema híbrido (reglas + TF-IDF + clasificación)."""

from fastapi import APIRouter

from api.schemas.hibrido_dto import ConsultaHibridaRequest
from api.services.hibrido import obtener_contexto, responder_consulta


router = APIRouter(prefix="/api/hibrido", tags=["sistema híbrido"])


@router.get("/contexto")
def contexto() -> dict:
    return obtener_contexto()


@router.post("/responder")
def responder(solicitud: ConsultaHibridaRequest) -> dict:
    return responder_consulta(solicitud)
