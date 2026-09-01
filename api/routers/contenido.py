"""Endpoints de código fuente explicado e informes académicos."""

from fastapi import APIRouter, HTTPException

from api.services.contenido import catalogo_semanas, obtener_codigo, obtener_informe


router = APIRouter(prefix="/api/contenido", tags=["contenido académico"])


@router.get("/semanas")
def semanas() -> dict:
    return catalogo_semanas()


@router.get("/codigo/{archivo_id}")
def codigo(archivo_id: str) -> dict:
    try:
        return obtener_codigo(archivo_id)
    except KeyError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except (FileNotFoundError, ValueError, SyntaxError) as error:
        raise HTTPException(status_code=503, detail=str(error)) from error


@router.get("/informes/{informe_id}")
def informe(informe_id: str) -> dict:
    try:
        return obtener_informe(informe_id)
    except KeyError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except (FileNotFoundError, ValueError) as error:
        raise HTTPException(status_code=503, detail=str(error)) from error
