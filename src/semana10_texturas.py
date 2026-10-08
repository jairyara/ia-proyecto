# Dashboard · Semana 10 — Regiones, intensidad y textura de paquetes
"""Extrae evidencia descriptiva de paquetes del piloto auditado (sin clasificar).

Ejecutar desde la raíz: python -m src.semana10_texturas
Solo se extraen descriptores de los 150 grupos de entrenamiento de Semana 8;
los 50 reservados se auditan para fijar la partición, pero no entran al análisis.
"""

from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
from skimage import filters, measure
from skimage.feature import local_binary_pattern

from src.vision.manifiesto import DEFAULT_RAIZ, ruta_segura
from src.vision.particion import preparar_piloto


ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS = ROOT / "artifacts"
RESULTADOS = ARTIFACTS / "semana10_resultados.json"
FIGURA = ARTIFACTS / "semana10_comparacion.png"
VECTORES = ARTIFACTS / "semana10_features.npy"
EJEMPLOS = {
    (clase, tipo): ARTIFACTS / f"semana10_{clase}_{tipo}.png"
    for clase in ("danado", "intacto") for tipo in ("gris", "mascara")
}
TAMANO = (480, 270)  # ancho, alto; conserva más detalle local que 16×16 del MLP.
RADIO = 2
PUNTOS = 16
BINS_INTENSIDAD = 32
AREA_MINIMA = 50  # píxeles a la resolución de análisis, no un tamaño físico.
VERSION_DESCRIPTOR = "semana10-paquetes-v1"


def extraer_caracteristicas(gris: np.ndarray, *, area_minima: int = AREA_MINIMA) -> tuple[np.ndarray, dict, np.ndarray, np.ndarray]:
    """Devuelve un vector 53D y medidas explicables de UNA imagen gris uint8."""
    if gris.ndim != 2 or gris.dtype != np.uint8 or min(gris.shape) < 16:
        raise ValueError("Se requiere imagen gris uint8 de al menos 16 píxeles por lado.")
    if area_minima < 0:
        raise ValueError("El filtro de área no puede ser negativo.")

    umbral = int(filters.threshold_otsu(gris))
    mascara = gris > umbral
    etiquetas = measure.label(mascara, connectivity=2)
    regiones = measure.regionprops(etiquetas)
    areas = np.asarray([region.area for region in regiones if region.area > area_minima], dtype=np.float64)
    pixeles = gris.size

    # Probabilidades (suma=1), no densidades de anchura 8 como en la clase.
    intensidad = np.histogram(gris, bins=BINS_INTENSIDAD, range=(0, 256))[0].astype(np.float64) / pixeles
    lbp = local_binary_pattern(gris, PUNTOS, RADIO, method="uniform")
    textura = np.bincount(lbp.astype(np.int64).ravel(), minlength=PUNTOS + 2).astype(np.float64)
    textura /= textura.sum()
    if len(textura) != PUNTOS + 2:
        raise ValueError("LBP produjo códigos fuera del rango uniforme esperado.")

    # Normalizar áreas por tamaño de imagen permite comparar distintas capturas.
    region = np.array([
        areas.mean() / pixeles if areas.size else 0.0,
        areas.std() / pixeles if areas.size else 0.0,
        float(areas.size),
    ])
    vector = np.concatenate((region, intensidad, textura))
    if vector.shape != (53,) or not np.isfinite(vector).all():
        raise ValueError("El descriptor no tiene 53 valores finitos.")
    metricas = {
        "umbral_otsu_0_255": umbral,
        "regiones_totales": len(regiones),
        "regiones_validas": int(areas.size),
        "area_media_porcentaje": round(float(region[0] * 100), 4),
        "area_desviacion_porcentaje": round(float(region[1] * 100), 4),
        "mascara_porcentaje": round(float(mascara.mean() * 100), 4),
        "sin_regiones_validas": not bool(areas.size),
        "histograma_intensidad": intensidad.round(8).tolist(),
        "histograma_lbp": textura.round(8).tolist(),
    }
    return vector, metricas, mascara, etiquetas


def leer_gris(ruta: Path) -> np.ndarray:
    """Mantiene el original intacto y fija una resolución reproducible."""
    with Image.open(ruta, formats=["PNG"]) as imagen:
        if imagen.mode != "RGB" or imagen.size != (960, 540):
            raise ValueError("El original no cumple el contrato RGB 960×540 del piloto.")
        return np.asarray(imagen.convert("L").resize(TAMANO, Image.Resampling.LANCZOS), dtype=np.uint8)


def _figura(ejemplos: list[tuple[dict, np.ndarray, np.ndarray, np.ndarray]], destino: Path) -> None:
    fig, axes = plt.subplots(2, 4, figsize=(16, 8), constrained_layout=True)
    for fila, (registro, gris, mascara, lbp) in enumerate(ejemplos):
        clase = registro["etiqueta"]
        axes[fila, 0].imshow(gris, cmap="gray", vmin=0, vmax=255)
        axes[fila, 0].set_title(f"{clase} · original gris")
        axes[fila, 1].imshow(mascara, cmap="gray", vmin=0, vmax=1)
        axes[fila, 1].set_title("Máscara Otsu · no es daño")
        axes[fila, 2].plot(np.arange(32) * 8 + 4, registro["histograma_intensidad"])
        axes[fila, 2].set_title("Intensidad · 32 probabilidades")
        axes[fila, 2].set_xlim(0, 256)
        axes[fila, 3].bar(range(PUNTOS + 2), registro["histograma_lbp"], width=0.8)
        axes[fila, 3].set_title("LBP uniforme · 18 probabilidades")
        for col in (0, 1):
            axes[fila, col].axis("off")
    destino.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(destino, dpi=130, metadata={"Software": "ia-proyecto / Semana 10"})
    plt.close(fig)


def ejecutar(*, resultados: Path = RESULTADOS, figura: Path = FIGURA, vectores: Path = VECTORES,
            raiz: Path = DEFAULT_RAIZ) -> dict:
    """Audita el piloto, extrae solo entrenamiento y guarda evidencia versionable."""
    particion = preparar_piloto(raiz)
    manifiesto = json.loads((ROOT / "data/manifests/piloto-visual-v1.json").read_text(encoding="utf-8"))
    registros = {item["id_origen"]: item for item in manifiesto["imagenes"]}
    filas: list[dict] = []
    matriz: list[np.ndarray] = []
    ejemplos: dict[str, tuple[dict, np.ndarray, np.ndarray, np.ndarray]] = {}

    for indice in particion.indices_train:
        muestra = particion.muestras[indice]
        origen = registros[muestra.id_origen]
        ruta = ruta_segura(raiz, origen["archivo"])
        if sha256(ruta.read_bytes()).hexdigest() != muestra.sha256:
            raise ValueError(f"Original modificado después de auditar: {muestra.id_origen}")
        gris = leer_gris(ruta)
        vector, metricas, mascara, _ = extraer_caracteristicas(gris)
        fila = {
            "id_origen": muestra.id_origen, "grupo_origen": muestra.grupo_origen,
            "etiqueta": muestra.etiqueta, "sha256_imagen": muestra.sha256,
            **metricas,
        }
        filas.append(fila)
        matriz.append(vector)
        if muestra.etiqueta not in ejemplos:
            aclarada = np.clip(gris.astype(np.int16) + 20, 0, 255).astype(np.uint8)
            vector_clara, metricas_claras, _, _ = extraer_caracteristicas(aclarada)
            fila["sensibilidad_mas_20_gris"] = {
                "delta_regiones_validas": metricas_claras["regiones_validas"] - metricas["regiones_validas"],
                "distancia_l1_intensidad": round(float(np.abs(vector_clara[3:35] - vector[3:35]).sum()), 6),
                "distancia_l1_lbp": round(float(np.abs(vector_clara[35:] - vector[35:]).sum()), 6),
            }
            ejemplos[muestra.etiqueta] = (fila, gris, mascara, vector[35:])

    if len(filas) != 150 or set(ejemplos) != {"danado", "intacto"}:
        raise ValueError("La partición de entrenamiento no coincide con el piloto 150/50.")
    datos = np.stack(matriz)
    if datos.shape != (150, 53):
        raise ValueError("La matriz de entrenamiento debe ser 150×53.")

    figura.parent.mkdir(parents=True, exist_ok=True)
    vectores.parent.mkdir(parents=True, exist_ok=True)
    resultados.parent.mkdir(parents=True, exist_ok=True)
    np.save(vectores, datos)
    _figura([ejemplos[clase] for clase in ("danado", "intacto")], figura)
    for clase in ("danado", "intacto"):
        fila, gris, mascara, _ = ejemplos[clase]
        Image.fromarray(gris).save(EJEMPLOS[(clase, "gris")])
        Image.fromarray(np.uint8(mascara) * 255).save(EJEMPLOS[(clase, "mascara")])
        fila["archivos_visuales"] = {
            tipo: {
                "archivo": EJEMPLOS[(clase, tipo)].name,
                "sha256": sha256(EJEMPLOS[(clase, tipo)].read_bytes()).hexdigest(),
            }
            for tipo in ("gris", "mascara")
        }
    resumen_clases = {}
    for clase in ("danado", "intacto"):
        grupo = [f for f in filas if f["etiqueta"] == clase]
        resumen_clases[clase] = {
            "n": len(grupo),
            "regiones_validas_mediana": float(np.median([f["regiones_validas"] for f in grupo])),
            "area_media_porcentaje_mediana": round(float(np.median([f["area_media_porcentaje"] for f in grupo])), 4),
            "sin_regiones_validas": sum(f["sin_regiones_validas"] for f in grupo),
        }
    salida = {
        "version_descriptor": VERSION_DESCRIPTOR,
        "sha256_codigo": sha256(Path(__file__).read_bytes()).hexdigest(),
        "origen": "Piloto académico sintético; no fotografías de envíos Amazon",
        "manifiesto_sha256": particion.manifiesto_sha256,
        "semilla_particion": particion.semilla,
        "entrenamiento": len(filas), "prueba_reservada_sin_descriptores": len(particion.indices_test),
        "dimensiones_original": [960, 540], "dimensiones_analisis": list(TAMANO),
        "conectividad": 8, "filtro_area_px": AREA_MINIMA,
        "lbp": {"radio": RADIO, "puntos": PUNTOS, "metodo": "uniform"},
        "vector": {"dimension": 53, "bloques": ["area_media_fraccion", "area_desviacion_fraccion", "numero_regiones", "intensidad_32_probabilidades", "lbp_18_probabilidades"]},
        "resumen_clases": resumen_clases,
        "ejemplos": [ejemplos[clase][0] for clase in ("danado", "intacto")],
        "ids_entrenamiento": [f["id_origen"] for f in filas],
        "sha256_figura": sha256(figura.read_bytes()).hexdigest(),
        "sha256_vectores": sha256(vectores.read_bytes()).hexdigest(),
        "advertencia": "Descriptor exploratorio: diferencias descriptivas no validan clasificación ni autorizan despacho o cuarentena.",
    }
    resultados.write_text(json.dumps(salida, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return salida


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raiz", type=Path, default=DEFAULT_RAIZ)
    args = parser.parse_args()
    resultado = ejecutar(raiz=args.raiz)
    print(json.dumps({k: resultado[k] for k in ("entrenamiento", "prueba_reservada_sin_descriptores", "resumen_clases", "ejemplos")}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
