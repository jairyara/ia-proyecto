# Dashboard · Semana 08 — Reconocimiento, evidencia y ontología
"""Semana 8, fase 1: entrada visual auditada y partición reproducible.

No entrena modelos, no escribe artefactos y no sustituye datos ausentes.
"""

from dataclasses import dataclass
from hashlib import sha256
from io import BytesIO
import json
from pathlib import Path

import numpy as np
from PIL import Image
from sklearn.model_selection import train_test_split

from src.vision.manifiesto import (
    DEFAULT_MANIFIESTO,
    DEFAULT_RAIZ,
    ErrorVisual,
    auditar_piloto,
    ruta_segura,
)


SEMILLA_PARTICION = 20260925
TAMANO_VECTOR = (16, 16)
CLASES = ("danado", "intacto")


@dataclass(frozen=True)
class MuestraVisual:
    id_origen: str
    grupo_origen: str
    etiqueta: str
    sha256: str
    vector: np.ndarray


@dataclass(frozen=True)
class ParticionVisual:
    muestras: tuple[MuestraVisual, ...]
    indices_train: tuple[int, ...]
    indices_test: tuple[int, ...]
    semilla: int
    tamano_vector: tuple[int, int]
    manifiesto_sha256: str

    @property
    def X_train(self) -> np.ndarray:
        return np.stack([self.muestras[i].vector for i in self.indices_train])

    @property
    def X_test(self) -> np.ndarray:
        return np.stack([self.muestras[i].vector for i in self.indices_test])

    @property
    def y_train(self) -> np.ndarray:
        return np.array([self.muestras[i].etiqueta for i in self.indices_train])

    @property
    def y_test(self) -> np.ndarray:
        return np.array([self.muestras[i].etiqueta for i in self.indices_test])

    def ids_por_split(self) -> dict[str, list[str]]:
        return {
            "train": [self.muestras[i].id_origen for i in self.indices_train],
            "test": [self.muestras[i].id_origen for i in self.indices_test],
        }


def vectorizar_png(contenido: bytes, tamano: tuple[int, int] = TAMANO_VECTOR) -> np.ndarray:
    """Convierte un PNG auditado a gris 16×16 y normaliza intensidades a [0, 1]."""
    if len(tamano) != 2 or any(type(valor) is not int or valor <= 0 for valor in tamano):
        raise ValueError("Tamaño de vector inválido.")
    with Image.open(BytesIO(contenido), formats=["PNG"]) as imagen:
        if imagen.mode != "RGB" or imagen.size != (960, 540):
            raise ErrorVisual("La imagen no conserva el formato visual auditado.")
        imagen.load()
        gris = imagen.convert("L").resize(tamano, Image.Resampling.LANCZOS)
        return np.asarray(gris, dtype=np.float32).reshape(-1) / np.float32(255.0)


def separar_grupos(
    muestras: tuple[MuestraVisual, ...], *, semilla: int = SEMILLA_PARTICION,
    fraccion_prueba: float = 0.25,
) -> tuple[tuple[int, ...], tuple[int, ...]]:
    """Estratifica grupos, no imágenes: ninguna identidad cruza los dos splits."""
    if not 0 < fraccion_prueba < 1:
        raise ValueError("La fracción de prueba debe estar entre 0 y 1.")
    etiquetas_grupo: dict[str, str] = {}
    for muestra in muestras:
        anterior = etiquetas_grupo.setdefault(muestra.grupo_origen, muestra.etiqueta)
        if anterior != muestra.etiqueta:
            raise ErrorVisual("Un grupo tiene etiquetas contradictorias.")
    if len(etiquetas_grupo) < 4 or set(etiquetas_grupo.values()) != set(CLASES):
        raise ErrorVisual("Se requieren grupos suficientes de ambas clases.")
    grupos = sorted(etiquetas_grupo)
    try:
        train, test = train_test_split(
            grupos, test_size=fraccion_prueba, random_state=semilla,
            stratify=[etiquetas_grupo[g] for g in grupos],
        )
    except ValueError as exc:
        raise ErrorVisual("No es posible estratificar los grupos de ambas clases.") from exc
    train_set, test_set = set(train), set(test)
    assert not train_set.intersection(test_set)
    return (
        tuple(i for i, muestra in enumerate(muestras) if muestra.grupo_origen in train_set),
        tuple(i for i, muestra in enumerate(muestras) if muestra.grupo_origen in test_set),
    )


def preparar_piloto(
    raiz: Path = DEFAULT_RAIZ, manifiesto: Path = DEFAULT_MANIFIESTO,
    *, semilla: int = SEMILLA_PARTICION,
) -> ParticionVisual:
    """Valida los originales fijados y prepara la entrada sin fallback ni escrituras."""
    contenido_manifiesto = manifiesto.read_bytes()
    esperado = json.loads(contenido_manifiesto)
    auditoria = auditar_piloto(raiz, manifiesto=esperado)
    muestras = []
    for registro in auditoria["imagenes"]:
        contenido = ruta_segura(raiz, registro["archivo"]).read_bytes()
        if sha256(contenido).hexdigest() != registro["sha256"]:
            raise ErrorVisual("La imagen cambió después de la auditoría.")
        muestras.append(MuestraVisual(
            id_origen=registro["id_origen"], grupo_origen=registro["grupo_origen"],
            etiqueta=registro["etiqueta"], sha256=registro["sha256"],
            vector=vectorizar_png(contenido),
        ))
    muestras_fijas = tuple(muestras)
    indices_train, indices_test = separar_grupos(muestras_fijas, semilla=semilla)
    return ParticionVisual(
        muestras=muestras_fijas, indices_train=indices_train, indices_test=indices_test,
        semilla=semilla, tamano_vector=TAMANO_VECTOR,
        manifiesto_sha256=sha256(contenido_manifiesto).hexdigest(),
    )
