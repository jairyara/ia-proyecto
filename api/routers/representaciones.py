"""Endpoints de representaciones numérica, simbólica y secuencial."""

from fastapi import APIRouter, HTTPException

from api.schemas.representaciones_dto import EvaluacionRepresentacionRequest
from api.services.representaciones import evaluar_representacion, obtener_contexto


router = APIRouter(prefix="/api/representaciones", tags=["representaciones"])


@router.get("/contexto")
def contexto() -> dict:
    try:
        return obtener_contexto()
    except (FileNotFoundError, ValueError) as error:
        raise HTTPException(status_code=503, detail=str(error)) from error


@router.post("/evaluar")
def evaluar(solicitud: EvaluacionRepresentacionRequest) -> dict:
    try:
        return evaluar_representacion(solicitud)
    except (FileNotFoundError, ValueError) as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
