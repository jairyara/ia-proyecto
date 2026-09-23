"""Mapa reproducible: dos RNG independientes; nunca usa etiquetas para muestrear."""

from dataclasses import asdict
from hashlib import sha256
import random

from src.datos.validacion import ManifiestoAmazon, validar_amazon
from src.vision.manifiesto import ErrorVisual, json_bytes


SEMILLA_PARADAS = 20260922
SEMILLA_IMAGENES = 20260923
ALGORITMO = "python314-random-sample-shuffle-v1"
AVISO = (
    "Imagen sintética de Industrial Quality Control of Packages v2, asociada "
    "aleatoriamente para demostración. No corresponde al envío original de Amazon."
)


def construir_mapa(csv: bytes, amazon: ManifiestoAmazon, visual: dict, visual_bytes: bytes,
                   *, version: str = "v1") -> dict:
    datos = validar_amazon(csv, amazon)
    pedidos = sorted(f["pedido_id"] for f in datos.filas)
    imagenes = sorted(i["id_origen"] for i in visual["imagenes"])
    if len(pedidos) < 200 or len(imagenes) != 200 or len(set(imagenes)) != 200:
        raise ErrorVisual("El piloto requiere 200 imágenes y al menos 200 paradas distintas.")
    if not version or len(version) > 73 or not version.isascii() or not all(c.isalnum() or c in "-_" for c in version):
        raise ErrorVisual("Versión de piloto inválida.")
    elegidos = random.Random(SEMILLA_PARADAS).sample(pedidos, 200)
    random.Random(SEMILLA_IMAGENES).shuffle(imagenes)
    return {
        "schema_version": 1, "version": version, "algoritmo": ALGORITMO,
        "semilla_paradas": SEMILLA_PARADAS, "semilla_imagenes": SEMILLA_IMAGENES,
        "amazon": asdict(amazon),
        "visual": {"fuente": visual["fuente_handle"], "version": str(visual["fuente_version"]),
                   "sha256": sha256(visual_bytes).hexdigest()},
        "aviso": AVISO,
        "asociaciones": sorted([
            {"pedido_id": p, "imagen_id_origen": i, "tipo_asociacion": "simulada"}
            for p, i in zip(elegidos, imagenes, strict=True)
        ], key=lambda a: a["pedido_id"]),
    }


def hash_mapa(mapa: dict) -> str:
    return sha256(json_bytes(mapa)).hexdigest()
