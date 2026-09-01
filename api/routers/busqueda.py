"""Endpoints de búsqueda heurística y replanificación."""

from fastapi import APIRouter, HTTPException

from api.schemas.busqueda_dto import ReplanificacionRequest, SimulacionBusquedaRequest
from api.services.busqueda import (
    listar_rutas_amazon,
    replanificar_busqueda,
    simular_busqueda,
)


router = APIRouter(prefix="/api/busqueda", tags=["búsqueda"])


@router.get("/amazon/rutas")
def rutas_amazon() -> dict:
    try:
        return {"rutas": listar_rutas_amazon()}
    except FileNotFoundError as error:
        raise HTTPException(status_code=503, detail=str(error)) from error


@router.post("/a-estrella/simular")
@router.post("/simular", include_in_schema=False)
def simular(solicitud: SimulacionBusquedaRequest) -> dict:
    try:
        return simular_busqueda(solicitud)
    except (FileNotFoundError, ValueError) as error:
        raise HTTPException(status_code=422, detail=str(error)) from error


@router.post("/replanificar")
def replanificar(solicitud: ReplanificacionRequest) -> dict:
    try:
        return replanificar_busqueda(solicitud)
    except (FileNotFoundError, ValueError) as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
