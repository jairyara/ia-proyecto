"""Utilidades de red y descarga HTTP con reintentos y tolerancia a fallos."""

from __future__ import annotations

import json
import time
import urllib.request


def descargar_json(url: str, timeout: int = 120, max_retries: int = 5, user_agent: str = "ia-proyecto/1.0") -> dict:
    """Descarga y deserializa un archivo JSON desde una URL HTTP/HTTPS con reintentos exponenciales."""
    ultimo_error = None
    for intento in range(1, max_retries + 1):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": user_agent})
            with urllib.request.urlopen(req, timeout=timeout) as response:
                contenido = response.read().decode("utf-8")
                return json.loads(contenido)
        except Exception as error:
            ultimo_error = error
            if intento < max_retries:
                time.sleep(2.0 * intento)
    raise RuntimeError(f"Fallo al descargar {url} tras {max_retries} intentos: {ultimo_error}")
