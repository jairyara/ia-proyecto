"""Regresión: importar y servir semanas anteriores no necesita persistencia."""

import os
from pathlib import Path
import subprocess
import sys
import unittest


class CompatibilidadHistoricaTests(unittest.TestCase):
    def test_api_funciona_sin_configuracion_bd_y_con_driver_bloqueado(self):
        codigo = '''
import sys
from unittest.mock import patch
from fastapi.testclient import TestClient
with patch("psycopg.connect", side_effect=AssertionError("BD prohibida")):
    from api.main import app
    assert "src.configuracion" not in sys.modules
    assert "src.persistencia.sesion" not in sys.modules
    with TestClient(app) as cliente:
        for ruta in ("/api/health", "/api/representaciones/contexto",
                     "/api/modelado/metricas", "/api/busqueda/amazon/rutas"):
            respuesta = cliente.get(ruta)
            assert respuesta.status_code == 200, (ruta, respuesta.status_code)
'''
        entorno = {k: v for k, v in os.environ.items()
                   if not k.startswith(("DB_", "POSTGRES_")) and k != "DATABASE_URL"}
        entorno["DATABASE_URL"] = "configuracion-invalida-no-debe-leerse"
        resultado = subprocess.run(
            [sys.executable, "-c", codigo], cwd=Path(__file__).resolve().parent.parent,
            env=entorno, capture_output=True, text=True, timeout=60,
        )
        self.assertEqual(resultado.returncode, 0, resultado.stdout + resultado.stderr)
