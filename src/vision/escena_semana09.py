# Dashboard · Semana 09 — Características, contornos y segmentación
"""Genera una escena logística original y sintética para la práctica de Semana 9."""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = ROOT / "data" / "imagen_proyecto.png"


def generar_escena(destino: Path = DEFAULT_OUTPUT) -> Path:
    """Dibuja un único paquete sobre una banda oscura, sin usar imágenes externas."""
    ancho, alto = 960, 540
    rng = np.random.default_rng(20260930)
    y, x = np.mgrid[:alto, :ancho]
    gradiente = 31 + 0.016 * x + 0.035 * y
    ruido = rng.normal(0, 2.2, (alto, ancho))
    rgb = np.stack((gradiente * .75, gradiente * .95, gradiente * 1.23), axis=2)
    rgb = np.uint8(np.clip(rgb + ruido[:, :, None], 0, 255))
    imagen = Image.fromarray(rgb, "RGB")
    dibujo = ImageDraw.Draw(imagen)

    # Banda transportadora: su superficie oscura crea un fondo contrastante.
    dibujo.polygon([(0, 376), (960, 328), (960, 535), (0, 540)], fill=(40, 52, 61))
    for i in range(0, 960, 93):
        dibujo.line([(i - 90, 410), (i + 90, 521)], fill=(68, 79, 87), width=3)
    dibujo.line([(0, 375), (960, 327)], fill=(91, 103, 109), width=8)

    # Sombra suave y paquete de cartón claro con tres caras distinguibles.
    sombra = Image.new("RGBA", (ancho, alto), (0, 0, 0, 0))
    d_sombra = ImageDraw.Draw(sombra)
    d_sombra.ellipse((183, 372, 800, 485), fill=(0, 0, 0, 170))
    imagen = Image.alpha_composite(imagen.convert("RGBA"), sombra.filter(ImageFilter.GaussianBlur(20)))
    dibujo = ImageDraw.Draw(imagen)
    dibujo.polygon([(218, 202), (626, 164), (767, 234), (356, 279)], fill=(225, 186, 128))
    dibujo.polygon([(356, 279), (767, 234), (762, 402), (353, 445)], fill=(200, 151, 91))
    dibujo.polygon([(218, 202), (356, 279), (353, 445), (216, 367)], fill=(165, 116, 70))
    dibujo.line([(218, 202), (626, 164), (767, 234), (762, 402), (353, 445), (216, 367), (218, 202)], fill=(92, 66, 48), width=4)
    dibujo.line([(218, 202), (356, 279), (353, 445)], fill=(92, 66, 48), width=4)
    dibujo.line([(356, 279), (767, 234)], fill=(92, 66, 48), width=4)

    # Cinta, etiqueta y rasgadura: detalles que producen bordes y agujeros en la máscara.
    dibujo.polygon([(441, 181), (480, 177), (618, 250), (576, 255)], fill=(240, 212, 159))
    dibujo.polygon([(576, 255), (618, 250), (615, 417), (574, 421)], fill=(228, 191, 136))
    dibujo.polygon([(405, 296), (527, 284), (525, 365), (404, 379)], fill=(236, 229, 208))
    dibujo.text((421, 305), "PKG-09 / REVISION", fill=(39, 47, 46))
    for offset, width in ((0, 3), (8, 2), (15, 4), (25, 2), (32, 3), (43, 2), (50, 4), (60, 2)):
        dibujo.rectangle((416 + offset, 334, 416 + offset + width, 357), fill=(42, 46, 44))
    dibujo.polygon([(684, 249), (711, 251), (703, 269), (720, 281), (691, 294), (685, 280), (672, 276)], fill=(74, 53, 43))
    dibujo.line([(684, 249), (711, 251), (703, 269), (720, 281), (691, 294)], fill=(110, 70, 48), width=3)

    destino.parent.mkdir(parents=True, exist_ok=True)
    imagen.convert("RGB").save(destino)
    return destino


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--salida", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    print(generar_escena(args.salida))


if __name__ == "__main__":
    main()
