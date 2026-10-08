# Dashboard · Semana 10 — Regiones, intensidad y textura de paquetes
"""Publica solo evidencia calculada offline y comprueba su integridad."""

from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse


ROOT = Path(__file__).resolve().parents[2]
RESULTADOS = ROOT / "artifacts/semana10_resultados.json"
FIGURA = ROOT / "artifacts/semana10_comparacion.png"
VECTORES = ROOT / "artifacts/semana10_features.npy"
MANIFIESTO = ROOT / "data/manifests/piloto-visual-v1.json"
CODIGO = ROOT / "src/semana10_texturas.py"
EJEMPLOS = {
    (clase, tipo): ROOT / f"artifacts/semana10_{clase}_{tipo}.png"
    for clase in ("danado", "intacto") for tipo in ("gris", "mascara")
}

router = APIRouter(prefix="/api/vision-semana10", tags=["Semana 10 · descriptores visuales"])


def _evidencia() -> dict:
    if not all(ruta.is_file() for ruta in (RESULTADOS, FIGURA, VECTORES, MANIFIESTO, CODIGO, *EJEMPLOS.values())):
        raise HTTPException(503, "Falta evidencia de Semana 10; ejecuta python -m src.semana10_texturas.")
    try:
        datos = json.loads(RESULTADOS.read_text(encoding="utf-8"))
        if (
            datos["version_descriptor"] != "semana10-paquetes-v1"
            or datos["entrenamiento"] != 150
            or datos["prueba_reservada_sin_descriptores"] != 50
            or datos["vector"]["dimension"] != 53
            or len(datos["ejemplos"]) != 2
            or len(datos["ids_entrenamiento"]) != 150
            or datos["manifiesto_sha256"] != sha256(MANIFIESTO.read_bytes()).hexdigest()
            or datos["sha256_codigo"] != sha256(CODIGO.read_bytes()).hexdigest()
            or datos["sha256_figura"] != sha256(FIGURA.read_bytes()).hexdigest()
            or datos["sha256_vectores"] != sha256(VECTORES.read_bytes()).hexdigest()
        ):
            raise ValueError("Evidencia obsoleta o inconsistente")
        ejemplos = {item["etiqueta"]: item for item in datos["ejemplos"]}
        if set(ejemplos) != {"danado", "intacto"}:
            raise ValueError("Faltan los dos ejemplos")
        for (clase, tipo), ruta in EJEMPLOS.items():
            referencia = ejemplos[clase]["archivos_visuales"][tipo]
            if referencia["archivo"] != ruta.name or referencia["sha256"] != sha256(ruta.read_bytes()).hexdigest():
                raise ValueError("Imagen de ejemplo obsoleta")
        return datos
    except (OSError, ValueError, KeyError, TypeError) as exc:
        raise HTTPException(503, "La evidencia de Semana 10 es inválida u obsoleta; regenérala.") from exc


@router.get("/resultados", summary="Consulta descriptores del piloto de entrenamiento")
def resultados() -> dict:
    return _evidencia()


@router.get("/evidencia", response_class=FileResponse,
            summary="Consulta comparación de dos paquetes de entrenamiento",
            responses={200: {"content": {"image/png": {}}}, 503: {"description": "Evidencia ausente u obsoleta"}})
def evidencia() -> FileResponse:
    _evidencia()
    return FileResponse(FIGURA, media_type="image/png", filename=FIGURA.name,
                        content_disposition_type="inline")


@router.get("/ejemplos/{clase}/{tipo}", response_class=FileResponse,
            summary="Consulta imagen gris o máscara Otsu de un ejemplo de entrenamiento",
            responses={200: {"content": {"image/png": {}}}, 404: {"description": "Tipo o clase no admitidos"}})
def ejemplo(clase: str, tipo: str) -> FileResponse:
    ruta = EJEMPLOS.get((clase, tipo))
    if ruta is None:
        raise HTTPException(404, "Solo se admiten danado/intacto y gris/mascara.")
    _evidencia()
    return FileResponse(ruta, media_type="image/png", filename=ruta.name,
                        content_disposition_type="inline")
