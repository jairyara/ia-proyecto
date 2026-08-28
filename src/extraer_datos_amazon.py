"""Punto de entrada CLI para la extracción de Amazon Last Mile (delegado a src.datos.amazon)."""

import sys
from src.datos.amazon import *  # noqa: F401, F403
from src.datos.amazon import main

if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
