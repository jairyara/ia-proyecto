from pathlib import Path
import tempfile
import unittest

import pandas as pd

from src.generador_pedidos import (
    DEFAULT_CASES,
    DEFAULT_SEED,
    FEATURE_COLUMNS,
    TARGET_COLUMN,
    generar_pedidos,
    guardar_pedidos,
)


class GeneradorTests(unittest.TestCase):
    def test_generacion_reproducible(self) -> None:
        a = generar_pedidos(casos=50, seed=123)
        b = generar_pedidos(casos=50, seed=123)
        pd.testing.assert_frame_equal(a, b)

    def test_columnas_esperadas(self) -> None:
        datos = generar_pedidos(casos=30, seed=1)
        columnas = ["pedido_id", *FEATURE_COLUMNS, TARGET_COLUMN]
        self.assertEqual(list(datos.columns), columnas)

    def test_objetivo_binaria(self) -> None:
        datos = generar_pedidos(casos=50, seed=1)
        self.assertTrue(datos[TARGET_COLUMN].isin([0, 1]).all())

    def test_rangos_plausibles(self) -> None:
        datos = generar_pedidos(casos=100, seed=1)
        self.assertTrue((datos["distancia_km"] >= 1).all())
        self.assertTrue((datos["volumen_m3"] > 0).all())
        self.assertTrue(datos["trafico_index"].between(0, 1).all())
        with self.assertRaises(ValueError):
            generar_pedidos(casos=10)

    def test_default_seed_usable(self) -> None:
        datos = generar_pedidos(casos=DEFAULT_CASES, seed=DEFAULT_SEED)
        self.assertEqual(len(datos), DEFAULT_CASES)


class PersistenciaTests(unittest.TestCase):
    def test_guardar_csv(self) -> None:
        datos = generar_pedidos(casos=25, seed=7)
        with tempfile.TemporaryDirectory() as directorio:
            ruta = Path(directorio) / "out.csv"
            guardar_pedidos(datos, ruta)
            self.assertTrue(ruta.exists())
            cargado = pd.read_csv(ruta)
            self.assertEqual(len(cargado), len(datos))


if __name__ == "__main__":
    unittest.main()
