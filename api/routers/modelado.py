"""Endpoints de inferencia y métricas del baseline supervisado."""

from fastapi import APIRouter, HTTPException

from api.schemas.modelado_dto import PedidoRequest
from api.services.modelado import obtener_metricas, predecir_riesgo


router = APIRouter(prefix="/api/modelado", tags=["aprendizaje supervisado"])


@router.get("/metricas")
def metricas() -> dict:
    try:
        return obtener_metricas()
    except (FileNotFoundError, ValueError) as error:
        raise HTTPException(status_code=503, detail=str(error)) from error


@router.post("/predecir-riesgo")
def predecir(solicitud: PedidoRequest) -> dict:
    try:
        return predecir_riesgo(solicitud)
    except (FileNotFoundError, ValueError) as error:
        raise HTTPException(status_code=503, detail=str(error)) from error
