"""MLP visual: métricas de prueba, línea base y artefactos verificables."""

from hashlib import sha256
import json

import pytest

from src.vision.modelo_mlp import entrenar_y_evaluar, guardar_resultado
from src.vision.particion import preparar_piloto


@pytest.fixture(scope="module")
def resultado_real():
    return entrenar_y_evaluar(preparar_piloto())


def test_mlp_evalua_solo_test_y_reporta_linea_base(resultado_real):
    meta = resultado_real.metadatos
    assert meta["particion"]["train"] == 150
    assert meta["particion"]["test"] == 50
    assert len(meta["predicciones_test"]) == 50
    assert set(meta["particion"]["ids"]["test"]) == {
        pred["id_origen"] for pred in meta["predicciones_test"]
    }
    assert meta["evaluacion"]["accuracy_baseline"] == 0.5
    assert sum(map(sum, meta["evaluacion"]["matriz_confusion"])) == 50
    assert all(0 <= pred["probabilidad_predicha"] <= 1 for pred in meta["predicciones_test"])


def test_artefactos_se_guardan_sin_sobrescribir(resultado_real, tmp_path):
    meta = guardar_resultado(resultado_real, tmp_path)
    assert sha256((tmp_path / "modelo_mlp_logistica.pkl").read_bytes()).hexdigest() == meta["modelo_sha256"]
    assert json.loads((tmp_path / "modelo_mlp_logistica.json").read_text()) == meta
    assert guardar_resultado(resultado_real, tmp_path) == meta
    (tmp_path / "modelo_mlp_logistica.json").write_text("alterado")
    with pytest.raises(FileExistsError):
        guardar_resultado(resultado_real, tmp_path)
