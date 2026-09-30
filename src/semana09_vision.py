# Dashboard · Semana 09 — Características, contornos y segmentación
"""Semana 09: inspección visual didáctica de un paquete logístico sintético.

Ejecutar desde la raíz: python -m src.semana09_vision
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
from skimage import color, feature, filters, measure


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_IMAGE = ROOT / "data" / "imagen_proyecto.png"
DEFAULT_FIGURE = ROOT / "artifacts" / "semana09_vision.png"
DEFAULT_RESULTS = ROOT / "artifacts" / "semana09_resultados.json"
SIGMAS = (1.0, 2.0, 4.0)


def analizar_imagen(ruta: Path) -> tuple[dict, np.ndarray, dict[float, np.ndarray], np.ndarray, np.ndarray]:
    """Calcula características, bordes, máscara Otsu y componentes conexas."""
    with Image.open(ruta) as entrada:
        rgb = np.asarray(entrada.convert("RGB"), dtype=np.uint8)
    if min(rgb.shape[:2]) < 16:
        raise ValueError("La imagen debe medir al menos 16 píxeles por lado.")

    gris = np.uint8(np.rint(color.rgb2gray(rgb) * 255))
    normalizada = gris.astype(np.float64) / 255.0
    bordes = {sigma: feature.canny(normalizada, sigma=sigma) for sigma in SIGMAS}
    umbral = int(filters.threshold_otsu(gris))
    # La caja es clara frente al fondo oscuro. Otsu se aplica a la imagen sin
    # suavizado Canny: sigma no altera esta máscara ni el número de regiones.
    mascara = gris > umbral
    etiquetas = measure.label(mascara, connectivity=2)
    areas = np.bincount(etiquetas.ravel())[1:]
    regiones_ordenadas = sorted(
        ({"etiqueta": int(i + 1), "area_px": int(area)} for i, area in enumerate(areas)),
        key=lambda region: region["area_px"], reverse=True,
    )
    resultado = {
        "imagen": "data/imagen_proyecto.png" if ruta.resolve() == DEFAULT_IMAGE else str(ruta),
        "sha256_imagen": sha256(ruta.read_bytes()).hexdigest(),
        "origen": "escena sintética propia; no fotografía ni envío Amazon",
        "ancho_px": int(rgb.shape[1]),
        "alto_px": int(rgb.shape[0]),
        "intensidad_media_0_255": round(float(gris.mean()), 2),
        "intensidad_desviacion_0_255": round(float(gris.std()), 2),
        "color_medio_rgb": [round(float(v), 2) for v in rgb.mean(axis=(0, 1))],
        "otsu_umbral_0_255": umbral,
        "mascara_pixeles": int(mascara.sum()),
        "mascara_porcentaje": round(float(mascara.mean() * 100), 2),
        "conectividad": 8,
        "regiones_conectadas": int(etiquetas.max()),
        "regiones_mayores": regiones_ordenadas[:5],
        "canny": [
            {"sigma": sigma, "pixeles_borde": int(bordes[sigma].sum()),
             "densidad_porcentaje": round(float(bordes[sigma].mean() * 100), 2)}
            for sigma in SIGMAS
        ],
    }
    return resultado, rgb, bordes, mascara, etiquetas


def guardar_figura(rgb: np.ndarray, bordes: dict[float, np.ndarray],
                   mascara: np.ndarray, etiquetas: np.ndarray,
                   umbral: int, destino: Path) -> None:
    """Conserva en un solo PNG las salidas que exige la rúbrica."""
    fig, axes = plt.subplots(2, 3, figsize=(15, 7.2), constrained_layout=True)
    paneles = [
        (rgb, "Imagen original · sintética", None),
        (bordes[1.0], "Canny · σ=1 (detalle)", "gray"),
        (bordes[2.0], "Canny · σ=2 (referencia)", "gray"),
        (bordes[4.0], "Canny · σ=4 (suavizado)", "gray"),
        (mascara, f"Máscara Otsu · t={umbral}/255", "gray"),
        (etiquetas, f"Regiones · {int(etiquetas.max())} componentes", "nipy_spectral"),
    ]
    for ax, (datos, titulo, mapa) in zip(axes.flat, paneles):
        ax.imshow(datos, cmap=mapa, vmin=0 if mapa == "gray" else None,
                  vmax=1 if mapa == "gray" else None)
        ax.set_title(titulo)
        ax.axis("off")
    destino.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(destino, dpi=140, metadata={"Software": "ia-proyecto / Semana 09"})
    plt.close(fig)


def ejecutar(imagen: Path = DEFAULT_IMAGE, figura: Path = DEFAULT_FIGURE,
            resultados: Path = DEFAULT_RESULTS) -> dict:
    if not imagen.is_file():
        raise FileNotFoundError(f"No existe la imagen: {imagen}")
    resumen, rgb, bordes, mascara, etiquetas = analizar_imagen(imagen)
    guardar_figura(rgb, bordes, mascara, etiquetas, resumen["otsu_umbral_0_255"], figura)
    resultados.parent.mkdir(parents=True, exist_ok=True)
    resultados.write_text(json.dumps(resumen, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return resumen


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--imagen", type=Path, default=DEFAULT_IMAGE)
    parser.add_argument("--figura", type=Path, default=DEFAULT_FIGURE)
    parser.add_argument("--resultados", type=Path, default=DEFAULT_RESULTS)
    args = parser.parse_args()
    print(json.dumps(ejecutar(args.imagen, args.figura, args.resultados), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
