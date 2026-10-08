"""Contrato numérico, partición e integridad de Semana 10."""

from __future__ import annotations

import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient
import numpy as np

from api.main import app
from api.routers import vision_semana10
from src.semana10_texturas import extraer_caracteristicas
from src.vision.particion import preparar_piloto


class Semana10Tests(unittest.TestCase):
    def test_vector_fijo_coherente_y_probabilidades(self):
        gris = np.tile(np.arange(64, dtype=np.uint8) * 4, (64, 1))
        uno, metricas, mascara, etiquetas = extraer_caracteristicas(gris)
        dos, _, _, _ = extraer_caracteristicas(gris)
        np.testing.assert_array_equal(uno, dos)
        self.assertEqual(uno.shape, (53,))
        self.assertTrue(np.isfinite(uno).all())
        self.assertAlmostEqual(float(uno[3:35].sum()), 1.0)
        self.assertAlmostEqual(float(uno[35:].sum()), 1.0)
        self.assertEqual(metricas["regiones_totales"], int(etiquetas.max()))
        self.assertEqual(metricas["mascara_porcentaje"], round(float(mascara.mean() * 100), 4))

    def test_sin_regiones_no_se_confunde_con_clase_intacta(self):
        gris = np.zeros((32, 32), dtype=np.uint8)
        vector, metricas, _, _ = extraer_caracteristicas(gris)
        self.assertEqual(vector[:3].tolist(), [0.0, 0.0, 0.0])
        self.assertTrue(metricas["sin_regiones_validas"])
        self.assertEqual(metricas["regiones_validas"], 0)
        with self.assertRaises(ValueError):
            extraer_caracteristicas(gris.astype(np.float64))
        with self.assertRaises(ValueError):
            extraer_caracteristicas(gris, area_minima=-1)

    def test_evidencia_real_usa_solo_entrenamiento_y_api_valida_hashes(self):
        cliente = TestClient(app)
        respuesta = cliente.get("/api/vision-semana10/resultados")
        self.assertEqual(respuesta.status_code, 200, respuesta.text)
        datos = respuesta.json()
        self.assertEqual((datos["entrenamiento"], datos["prueba_reservada_sin_descriptores"]), (150, 50))
        self.assertEqual([x["etiqueta"] for x in datos["ejemplos"]], ["danado", "intacto"])
        self.assertEqual(len(set(datos["ids_entrenamiento"])), 150)
        particion = preparar_piloto()
        self.assertEqual(set(datos["ids_entrenamiento"]), set(particion.ids_por_split()["train"]))
        self.assertFalse(set(datos["ids_entrenamiento"]) & set(particion.ids_por_split()["test"]))
        self.assertEqual(np.load("artifacts/semana10_features.npy", allow_pickle=False).shape, (150, 53))
        figura = cliente.get("/api/vision-semana10/evidencia")
        self.assertEqual(figura.headers["content-type"], "image/png")
        self.assertIn("inline", figura.headers["content-disposition"])
        for clase in ("danado", "intacto"):
            for tipo in ("gris", "mascara"):
                ejemplo = cliente.get(f"/api/vision-semana10/ejemplos/{clase}/{tipo}")
                self.assertEqual(ejemplo.headers["content-type"], "image/png")
                self.assertIn("inline", ejemplo.headers["content-disposition"])
        self.assertEqual(cliente.get("/api/vision-semana10/ejemplos/otro/gris").status_code, 404)

        with TemporaryDirectory() as temporal:
            invalido = Path(temporal) / "resultados.json"
            datos["sha256_figura"] = "0" * 64
            invalido.write_text(json.dumps(datos), encoding="utf-8")
            with patch.object(vision_semana10, "RESULTADOS", invalido):
                self.assertEqual(cliente.get("/api/vision-semana10/resultados").status_code, 503)
                self.assertEqual(cliente.get("/api/vision-semana10/evidencia").status_code, 503)


if __name__ == "__main__":
    unittest.main()
