"""Semana 11: cuarteto logístico, separación de datos y evidencia HTTP."""

from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path

from fastapi.testclient import TestClient
import pandas as pd
import pytest
from sklearn.model_selection import StratifiedGroupKFold

from api.main import app
from src.semana11_benchmark import DEFAULT_INPUT, MODEL_NAMES, SEED, ejecutar


def test_cuarteto_y_metadatos_reproducibles(tmp_path: Path) -> None:
    csv = tmp_path / "benchmark.csv"
    meta = tmp_path / "benchmark.json"
    tabla = ejecutar(DEFAULT_INPUT, csv, meta)
    assert tuple(tabla.modelo) == MODEL_NAMES
    assert len(tabla) == 4
    assert tabla["accuracy"].between(0, 1).all()
    assert tabla["recall_retraso"].between(0, 1).all()
    assert (tabla["fit_seconds"] > 0).all()
    assert (tabla["infer_ms_por_pedido_p95"] > 0).all()
    evidencia = json.loads(meta.read_text())
    assert (evidencia["n_raw"], evidencia["n_excluded_station"], evidencia["n_total"]) == (14411, 100, 14311)
    assert (evidencia["n_train"], evidencia["n_test"]) == (10802, 3509)
    assert (evidencia["n_routes_train"], evidencia["n_routes_test"]) == (76, 24)
    assert evidencia["target"] == "retrasado_estimado"
    assert "secuencia_real" not in evidencia["variables"]
    assert "route_id" not in evidencia["variables"]
    assert evidencia["sha256_csv"] == sha256(csv.read_bytes()).hexdigest()
    assert evidencia["sha256_dataset"] == sha256(DEFAULT_INPUT.read_bytes()).hexdigest()
    assert set(evidencia["modelos"]) == set(MODEL_NAMES)
    # El reloj varía: las métricas, umbrales y matrices no deben variar con la misma semilla.
    generado = pd.read_csv(csv)
    for columna in ("accuracy", "recall_retraso", "falsos_negativos", "umbral"):
        assert generado[columna].tolist() == tabla[columna].tolist()


def test_rechaza_etiquetas_o_variables_incompletas(tmp_path: Path) -> None:
    datos = pd.read_csv(DEFAULT_INPUT)
    datos.loc[1, "tiempo_servicio_seg"] = None
    entrada = tmp_path / "incompleto.csv"
    datos.to_csv(entrada, index=False)
    with pytest.raises(ValueError, match="faltantes"):
        ejecutar(entrada, tmp_path / "out.csv", tmp_path / "out.json")


def test_etiqueta_amazon_es_una_regla_y_no_retraso_observado() -> None:
    datos = pd.read_csv(DEFAULT_INPUT)
    entregas = datos.loc[datos.tipo_parada == "Dropoff"]
    regla_sin_secuencia = (
        ((entregas.tiempo_servicio_seg > 150) & (entregas.volumen_total_m3 > 0.03))
        | ((entregas.distancia_deposito_km > 15) & (entregas.num_paquetes >= 3))
    ).astype(int)
    # En esta muestra, la cláusula con secuencia_real no aporta positivos exclusivos.
    assert regla_sin_secuencia.eq(entregas.retrasado_estimado).all()


def test_particion_reserva_rutas_completas() -> None:
    datos = pd.read_csv(DEFAULT_INPUT)
    entregas = datos.loc[datos.tipo_parada == "Dropoff"].reset_index(drop=True)
    train, test = next(StratifiedGroupKFold(n_splits=4, shuffle=True, random_state=SEED).split(
        entregas, entregas.retrasado_estimado, entregas.route_id,
    ))
    assert len(train) == 10802 and len(test) == 3509
    assert set(entregas.route_id.iloc[train]).isdisjoint(entregas.route_id.iloc[test])


def test_api_expone_evidencia_y_detecta_obsolescencia(monkeypatch, tmp_path: Path) -> None:
    from api.routers import semana11

    cliente = TestClient(app)
    respuesta = cliente.get("/api/semana11/benchmark")
    assert respuesta.status_code == 200
    assert [fila["modelo"] for fila in respuesta.json()["resultados"]] == list(MODEL_NAMES)
    copia = tmp_path / "benchmark.csv"
    copia.write_bytes(semana11.CSV.read_bytes() + b"\n")
    monkeypatch.setattr(semana11, "CSV", copia)
    assert cliente.get("/api/semana11/benchmark").status_code == 503
