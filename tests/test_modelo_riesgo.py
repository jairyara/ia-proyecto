from pathlib import Path
import tempfile
import unittest

import pandas as pd

from src.generador_pedidos import generar_pedidos
from src.modelo_riesgo import (
    TARGET,
    cargar_pedidos,
    entrenar_y_evaluar,
    render_report,
)


class ModeloTests(unittest.TestCase):
    def setUp(self) -> None:
        self.datos = generar_pedidos(casos=200, seed=20260828)

    def test_pipeline_completo(self) -> None:
        resultados, mejor, _ = entrenar_y_evaluar(self.datos)
        self.assertIn("logistic_regression", resultados)
        self.assertIn("random_forest", resultados)
        self.assertIn(mejor, resultados)
        for nombre, metricas in resultados.items():
            self.assertIn("accuracy", metricas)
            self.assertIn("f1", metricas)
            self.assertEqual(len(metricas["matriz_confusion"]), 2)

    def test_metricas_en_rango(self) -> None:
        resultados, _, _ = entrenar_y_evaluar(self.datos)
        for nombre, metricas in resultados.items():
            self.assertGreaterEqual(metricas["accuracy"], 0.0)
            self.assertLessEqual(metricas["accuracy"], 1.0)
            self.assertGreaterEqual(metricas["f1"], 0.0)
            self.assertLessEqual(metricas["f1"], 1.0)

    def test_reporte_contiene_secciones(self) -> None:
        resultados, mejor, _ = entrenar_y_evaluar(self.datos)
        reporte = render_report(resultados, mejor, "fuente", "archivo.csv")
        self.assertIn("Baseline supervisado", reporte)
        self.assertIn("Modelo elegido", reporte)

    def test_carga_dataset_real(self) -> None:
        ruta = Path(__file__).resolve().parent.parent / "data" / "pedidos.csv"
        datos = cargar_pedidos(ruta)
        self.assertGreaterEqual(len(datos), 200)
        self.assertIn(TARGET, datos.columns)


if __name__ == "__main__":
    unittest.main()
