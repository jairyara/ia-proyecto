"""Punto de entrada CLI para la generación de pedidos sintéticos (delegado a src.datos.sintetico)."""

import sys
from src.datos.sintetico import *  # noqa: F401, F403
from src.datos.sintetico import main

if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
