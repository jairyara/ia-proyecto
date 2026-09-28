# Dashboard · Semana 08 — Reconocimiento, evidencia y ontología
"""Semana 8, fase 2: evaluación honesta del MLP visual y línea base."""

from dataclasses import dataclass
from hashlib import sha256
import json
from pathlib import Path
import pickle

import numpy as np
from sklearn.dummy import DummyClassifier
from sklearn.exceptions import ConvergenceWarning
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.neural_network import MLPClassifier
import warnings

from src.vision.particion import CLASES, ParticionVisual


VERSION_MODELO = "mlp-visual-v1"
PARAMETROS_MLP = {"hidden_layer_sizes": (64,), "max_iter": 400, "random_state": 42}


@dataclass(frozen=True)
class ResultadoMLP:
    modelo: MLPClassifier
    metadatos: dict


def entrenar_y_evaluar(particion: ParticionVisual) -> ResultadoMLP:
    """Entrena solo con train y evalúa una vez en el conjunto reservado."""
    X_train, X_test = particion.X_train, particion.X_test
    y_train, y_test = particion.y_train, particion.y_test
    if X_train.shape[1] != 256 or X_test.shape[1] != 256:
        raise ValueError("El MLP v1 requiere vectores de 16×16 píxeles.")

    baseline = DummyClassifier(strategy="most_frequent")
    baseline.fit(X_train, y_train)
    modelo = MLPClassifier(**PARAMETROS_MLP)
    with warnings.catch_warnings(record=True) as avisos:
        warnings.simplefilter("always", ConvergenceWarning)
        modelo.fit(X_train, y_train)
    pred = modelo.predict(X_test)
    probabilidades = modelo.predict_proba(X_test)
    clases = list(modelo.classes_)
    metadatos = {
        "version": VERSION_MODELO,
        "dataset_manifiesto_sha256": particion.manifiesto_sha256,
        "particion": {"semilla": particion.semilla, "train": len(y_train), "test": len(y_test),
                      "ids": particion.ids_por_split(),
                      "conteos": {split: {clase: int(np.sum(y == clase)) for clase in CLASES}
                                  for split, y in (("train", y_train), ("test", y_test))}},
        "preprocesamiento": {"modo": "L", "ancho": 16, "alto": 16,
                             "remuestreo": "LANCZOS", "normalizacion": "valor/255"},
        "modelo": {"algoritmo": "MLPClassifier", **PARAMETROS_MLP,
                   "hidden_layer_sizes": list(PARAMETROS_MLP["hidden_layer_sizes"]),
                   "iteraciones": int(modelo.n_iter_),
                   "convergencia_advertida": any(issubclass(a.category, ConvergenceWarning) for a in avisos)},
        "evaluacion": {
            "accuracy": float(accuracy_score(y_test, pred)),
            "accuracy_baseline": float(accuracy_score(y_test, baseline.predict(X_test))),
            "clases": list(CLASES),
            "matriz_confusion": confusion_matrix(y_test, pred, labels=CLASES).tolist(),
            "por_clase": classification_report(y_test, pred, labels=CLASES,
                                                output_dict=True, zero_division=0),
        },
        "predicciones_test": [
            {"id_origen": particion.muestras[i].id_origen,
             "etiqueta_real": particion.muestras[i].etiqueta,
             "clase_predicha": str(clase),
             "probabilidad_predicha": float(probabilidades[pos, clases.index(clase)])}
            for pos, (i, clase) in enumerate(zip(particion.indices_test, pred, strict=True))
        ],
    }
    return ResultadoMLP(modelo=modelo, metadatos=metadatos)


def guardar_resultado(resultado: ResultadoMLP, carpeta: Path) -> dict:
    """Publica artefactos propios; una versión existente distinta nunca se pisa."""
    carpeta.mkdir(parents=True, exist_ok=True)
    modelo_path = carpeta / "modelo_mlp_logistica.pkl"
    informe_path = carpeta / "modelo_mlp_logistica.json"
    modelo_bytes = pickle.dumps(resultado.modelo, protocol=pickle.HIGHEST_PROTOCOL)
    metadatos = {**resultado.metadatos, "modelo_sha256": sha256(modelo_bytes).hexdigest()}
    informe_bytes = (json.dumps(metadatos, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode()
    archivos = ((modelo_path, modelo_bytes), (informe_path, informe_bytes))
    for ruta, contenido in archivos:
        if ruta.exists():
            if ruta.read_bytes() != contenido:
                raise FileExistsError(f"Artefacto existente distinto: {ruta.name}; usar otra versión.")
    for ruta, contenido in archivos:
        if not ruta.exists():
            ruta.write_bytes(contenido)
    return metadatos
