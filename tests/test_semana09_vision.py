"""Regresiones de la práctica de visión y su API de evidencia."""

from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient
from PIL import Image

from api.main import app
from api.routers import vision_semana09
from src.semana09_vision import analizar_imagen, ejecutar
from src.vision.escena_semana09 import generar_escena


class Semana09VisionTests(unittest.TestCase):
    def test_escena_es_propia_y_determinista(self):
        with TemporaryDirectory() as temporal:
            primera = Path(temporal) / "uno.png"
            segunda = Path(temporal) / "dos.png"
            generar_escena(primera)
            generar_escena(segunda)
            self.assertEqual(sha256(primera.read_bytes()).digest(), sha256(segunda.read_bytes()).digest())
            with Image.open(primera) as imagen:
                self.assertEqual(imagen.size, (960, 540))

    def test_pipeline_expone_canny_otsu_mascara_y_regiones(self):
        with TemporaryDirectory() as temporal:
            ruta = Path(temporal)
            imagen = generar_escena(ruta / "paquete.png")
            figura = ruta / "evidencia.png"
            json_path = ruta / "resultado.json"
            resultado = ejecutar(imagen, figura, json_path)
            self.assertTrue(figura.is_file())
            self.assertEqual(json.loads(json_path.read_text())["sha256_imagen"], sha256(imagen.read_bytes()).hexdigest())
            self.assertEqual(resultado["otsu_umbral_0_255"], 105)
            self.assertEqual(resultado["regiones_conectadas"], 2)
            self.assertEqual(resultado["conectividad"], 8)
            self.assertEqual([item["sigma"] for item in resultado["canny"]], [1.0, 2.0, 4.0])
            self.assertGreater(resultado["canny"][0]["pixeles_borde"], resultado["canny"][-1]["pixeles_borde"])
            _, _, _, mascara, etiquetas = analizar_imagen(imagen)
            self.assertEqual(int(mascara.sum()), resultado["mascara_pixeles"])
            self.assertEqual(int(etiquetas.max()), resultado["regiones_conectadas"])

    def test_api_publica_evidencia_y_rechaza_hash_obsoleto(self):
        cliente = TestClient(app)
        respuesta = cliente.get("/api/vision-semana09/resultados")
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(respuesta.json()["otsu_umbral_0_255"], 105)
        figura = cliente.get("/api/vision-semana09/evidencia")
        self.assertEqual(figura.headers["content-type"], "image/png")
        self.assertIn("inline", figura.headers["content-disposition"])
        self.assertEqual(cliente.get("/api/vision-semana09/imagen").headers["content-type"], "image/png")
        with TemporaryDirectory() as temporal:
            obsoleto = Path(temporal) / "resultados.json"
            datos = respuesta.json()
            datos["sha256_imagen"] = "0" * 64
            obsoleto.write_text(json.dumps(datos), encoding="utf-8")
            with patch.object(vision_semana09, "RESULTADOS", obsoleto):
                self.assertEqual(cliente.get("/api/vision-semana09/resultados").status_code, 503)


if __name__ == "__main__":
    unittest.main()
