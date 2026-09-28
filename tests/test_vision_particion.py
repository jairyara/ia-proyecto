"""Fase 1 de Semana 8: los datos ausentes no se inventan y los grupos no fugan."""

from dataclasses import replace
from pathlib import Path

import numpy as np
import pytest

from src.vision.manifiesto import ErrorVisual
from src.vision.particion import MuestraVisual, preparar_piloto, separar_grupos


def _muestras() -> tuple[MuestraVisual, ...]:
    return tuple(
        MuestraVisual(f"{grupo}_{vista}", grupo, etiqueta, "a" * 64, np.zeros(256))
        for etiqueta in ("danado", "intacto")
        for numero in range(8)
        for grupo in (f"{etiqueta}-{numero}",)
        for vista in ("side", "top")
    )


def test_particion_por_grupo_es_reproducible_y_estratificada():
    muestras = _muestras()
    train, test = separar_grupos(muestras, semilla=42)
    assert (train, test) == separar_grupos(muestras, semilla=42)
    assert len(train) == 24 and len(test) == 8
    assert {muestras[i].grupo_origen for i in train}.isdisjoint(
        {muestras[i].grupo_origen for i in test}
    )
    assert {clase: sum(muestras[i].etiqueta == clase for i in test) for clase in ("danado", "intacto")} == {
        "danado": 4, "intacto": 4,
    }


def test_particion_rechaza_etiquetas_contradictorias():
    muestras = _muestras()
    incorrecta = replace(muestras[1], etiqueta="intacto")
    with pytest.raises(ErrorVisual, match="contradictorias"):
        separar_grupos((muestras[0], incorrecta, *muestras[2:]))


def test_piloto_real_tiene_200_vectores_y_ningun_grupo_cruzado():
    particion = preparar_piloto()
    assert len(particion.muestras) == 200
    assert particion.X_train.shape == (150, 256)
    assert particion.X_test.shape == (50, 256)
    assert set(particion.y_train) == set(particion.y_test) == {"danado", "intacto"}
    assert np.min(particion.X_train) >= 0 and np.max(particion.X_train) <= 1
    assert np.all(np.isfinite(particion.X_test))
    assert {particion.muestras[i].grupo_origen for i in particion.indices_train}.isdisjoint(
        {particion.muestras[i].grupo_origen for i in particion.indices_test}
    )
    assert preparar_piloto().ids_por_split() == particion.ids_por_split()


def test_piloto_ausente_falla_sin_sustituirlo(tmp_path: Path):
    with pytest.raises((OSError, ErrorVisual)):
        preparar_piloto(raiz=tmp_path)
