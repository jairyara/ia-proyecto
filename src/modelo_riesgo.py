"""Punto de entrada CLI para el modelo de riesgo de retraso (delegado a src.modelado.riesgo_retraso)."""

import sys
from src.modelado.riesgo_retraso import *  # noqa: F401, F403
from src.modelado.riesgo_retraso import main

if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
