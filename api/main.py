"""Aplicación FastAPI y servidor estático de la SPA compilada."""

from __future__ import annotations

import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, Response
from fastapi.staticfiles import StaticFiles

from api.routers import busqueda, clasificacion, contenido, hibrido, modelado


ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / "dashboard" / "dist"

app = FastAPI(
    title="API · Sistema inteligente para logística",
    version="1.0.0",
    description="Trazabilidad de búsqueda, riesgo supervisado y reglas simbólicas.",
)

origenes = [
    origen.strip()
    for origen in os.getenv(
        "DASHBOARD_CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173"
    ).split(",")
    if origen.strip()
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origenes,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)

app.include_router(busqueda.router)
app.include_router(modelado.router)
app.include_router(clasificacion.router)
app.include_router(hibrido.router)
app.include_router(contenido.router)


@app.get("/api/health", tags=["sistema"])
def health() -> dict[str, str]:
    return {"estado": "ok", "servicio": "dashboard-ia-logistica"}


if DIST.exists():
    app.mount("/assets", StaticFiles(directory=DIST / "assets"), name="assets")

    @app.get("/{ruta:path}", include_in_schema=False)
    def spa(ruta: str) -> FileResponse:
        candidato = (DIST / ruta).resolve()
        if ruta and candidato.is_relative_to(DIST.resolve()) and candidato.is_file():
            return FileResponse(candidato)
        return FileResponse(DIST / "index.html")

    @app.head("/{ruta:path}", include_in_schema=False)
    def spa_head(ruta: str) -> Response:
        return Response(status_code=200)
else:

    @app.get("/", include_in_schema=False)
    def raiz() -> dict[str, str]:
        return {
            "mensaje": "API del dashboard activa",
            "documentacion": "/docs",
            "frontend": "Ejecuta `pnpm dev` dentro de dashboard/.",
        }
