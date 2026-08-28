"""Pruebas unitarias para el módulo común (geo y red)."""

from __future__ import annotations

import unittest
from unittest.mock import MagicMock, patch

from src.comun.geo import haversine_km
from src.comun.red import descargar_json


class GeoTests(unittest.TestCase):
    def test_haversine_mismas_coordenadas(self) -> None:
        self.assertAlmostEqual(haversine_km(10.0, -75.0, 10.0, -75.0), 0.0)

    def test_haversine_distancia_positiva(self) -> None:
        dist = haversine_km(4.6097, -74.0817, 6.2442, -75.5812)  # Bogotá - Medellín ~240 km
        self.assertGreater(dist, 200.0)
        self.assertLess(dist, 300.0)


class RedTests(unittest.TestCase):
    @patch("urllib.request.urlopen")
    def test_descarga_json_exitoso(self, mock_urlopen: MagicMock) -> None:
        mock_response = MagicMock()
        mock_response.read.return_value = b'{"status": "ok", "count": 42}'
        mock_response.__enter__.return_value = mock_response
        mock_urlopen.return_value = mock_response

        datos = descargar_json("https://example.com/data.json")
        self.assertEqual(datos, {"status": "ok", "count": 42})


if __name__ == "__main__":
    unittest.main()
