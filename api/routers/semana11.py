# Dashboard · Semana 11 — Benchmark y decisión de arquitectura
"""Lectura de evidencia offline; la API nunca entrena modelos durante una solicitud."""

from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path

import pandas as pd
from fastapi import APIRouter, HTTPException


ROOT = Path(__file__).resolve().parents[2]
CSV = ROOT / "artifacts/benchmark.csv"
META = ROOT / "artifacts/semana11_benchmark.json"
DATOS = ROOT / "data/amazon_pedidos.csv"
CODIGO = ROOT / "src/semana11_benchmark.py"
MODELOS = ["logistic", "forest", "mlp", "hist"]

router = APIRouter(prefix="/api/semana11", tags=["Semana 11 · benchmark logístico"])


@router.get("/benchmark", summary="Consulta benchmark de cuatro modelos sobre riesgo heurístico Amazon")
def benchmark() -> dict:
    if not all(ruta.is_file() for ruta in (CSV, META, DATOS, CODIGO)):
        raise HTTPException(503, "Falta evidencia; ejecuta python -m src.semana11_benchmark.")
    try:
        evidencia = json.loads(META.read_text(encoding="utf-8"))
        tabla = pd.read_csv(CSV)
        if (
            evidencia["version"] != 2
            or evidencia["sha256_csv"] != sha256(CSV.read_bytes()).hexdigest()
            or evidencia["sha256_dataset"] != sha256(DATOS.read_bytes()).hexdigest()
            or evidencia["sha256_codigo"] != sha256(CODIGO.read_bytes()).hexdigest()
            or evidencia["n_total"] != evidencia["n_train"] + evidencia["n_test"]
            or tabla["modelo"].tolist() != MODELOS
            or tabla.isna().any().any()
        ):
            raise ValueError("Evidencia incompleta u obsoleta")
        return {"evidencia": evidencia, "resultados": tabla.to_dict(orient="records")}
    except (OSError, ValueError, KeyError, TypeError) as error:
        raise HTTPException(503, "Evidencia inválida u obsoleta; regenera el benchmark.") from error
