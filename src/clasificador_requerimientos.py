"""Punto de entrada CLI para el clasificador de requerimientos (delegado a src.clasificacion.requerimientos)."""

import sys
from src.clasificacion.requerimientos import *  # noqa: F401, F403
from src.clasificacion.requerimientos import main

if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
