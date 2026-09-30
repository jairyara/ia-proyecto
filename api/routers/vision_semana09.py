# Dashboard · Semana 09 — Características, contornos y segmentación
"""Resultados versionados de la práctica visual de Semana 9."""

from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field


ROOT = Path(__file__).resolve().parents[2]
IMAGEN = ROOT / "data" / "imagen_proyecto.png"
RESULTADOS = ROOT / "artifacts" / "semana09_resultados.json"
EVIDENCIA = ROOT / "artifacts" / "semana09_vision.png"

router = APIRouter(prefix="/api/vision-semana09", tags=["Semana 9 · visión"])


class BordeSigma(BaseModel):
    sigma: float
    pixeles_borde: int
    densidad_porcentaje: float


class Region(BaseModel):
    etiqueta: int
    area_px: int


class ResultadosVision(BaseModel):
    imagen: str
    sha256_imagen: str
    origen: str
    ancho_px: int
    alto_px: int
    intensidad_media_0_255: float
    intensidad_desviacion_0_255: float
    color_medio_rgb: list[float] = Field(min_length=3, max_length=3)
    otsu_umbral_0_255: int
    mascara_pixeles: int
    mascara_porcentaje: float
    conectividad: int
    regiones_conectadas: int
    regiones_mayores: list[Region]
    canny: list[BordeSigma]


@router.get("/resultados", response_model=ResultadosVision,
            summary="Consulta métricas verificadas de Canny, Otsu y regiones",
            responses={503: {"description": "Evidencia ausente, inválida u obsoleta"}})
def resultados() -> ResultadosVision:
    """Lee la evidencia calculada offline; nunca inventa métricas al abrir la UI."""
    if not RESULTADOS.is_file() or not IMAGEN.is_file():
        raise HTTPException(503, "Falta la evidencia de Semana 9; ejecuta python -m src.semana09_vision.")
    try:
        datos = json.loads(RESULTADOS.read_text(encoding="utf-8"))
        if datos["sha256_imagen"] != sha256(IMAGEN.read_bytes()).hexdigest():
            raise HTTPException(503, "La imagen cambió; regenera la evidencia de Semana 9.")
        return ResultadosVision.model_validate(datos)
    except (OSError, ValueError, KeyError) as exc:
        raise HTTPException(503, "La evidencia de Semana 9 es inválida; regenera los resultados.") from exc


@router.get("/evidencia", response_class=FileResponse,
            summary="Consulta la figura comparativa original/Canny/Otsu/regiones",
            responses={200: {"content": {"image/png": {}}},
                       503: {"description": "Figura aún no generada"}})
def evidencia() -> FileResponse:
    if not EVIDENCIA.is_file():
        raise HTTPException(503, "Falta la figura de Semana 9; ejecuta python -m src.semana09_vision.")
    return FileResponse(EVIDENCIA, media_type="image/png", filename="semana09_vision.png",
                        content_disposition_type="inline")


@router.get("/imagen", response_class=FileResponse,
            summary="Consulta la escena sintética de entrada",
            responses={200: {"content": {"image/png": {}}},
                       503: {"description": "Imagen de entrada ausente"}})
def imagen() -> FileResponse:
    if not IMAGEN.is_file():
        raise HTTPException(503, "Falta la imagen de entrada de Semana 9.")
    return FileResponse(IMAGEN, media_type="image/png", filename="imagen_proyecto.png",
                        content_disposition_type="inline")
