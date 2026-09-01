"""Pruebas del catálogo didáctico de código e informes."""

from __future__ import annotations

import unittest

from api.services.contenido import (
    catalogo_semanas,
    fragmento_traza,
    obtener_codigo,
    obtener_informe,
)


class CatalogoContenidoTests(unittest.TestCase):
    def test_semanas_se_exponen_en_orden_ascendente(self):
        catalogo = catalogo_semanas()["semanas"]

        self.assertEqual([semana["numero"] for semana in catalogo], [2, 3, 4])

    def test_cada_archivo_registrado_tiene_explicacion_por_linea(self):
        for semana in catalogo_semanas()["semanas"]:
            for ejercicio in semana["ejercicios"]:
                for archivo in ejercicio["archivos"]:
                    with self.subTest(archivo=archivo["id"]):
                        documento = obtener_codigo(archivo["id"])
                        self.assertGreater(documento["total_lineas"], 0)
                        self.assertEqual(documento["total_lineas"], len(documento["lineas"]))
                        self.assertTrue(all(linea["explicacion"] for linea in documento["lineas"]))
                        self.assertTrue(documento["hash"])

    def test_cada_informe_registrado_se_puede_navegar(self):
        for semana in catalogo_semanas()["semanas"]:
            for informe in semana["informes"]:
                with self.subTest(informe=informe["id"]):
                    documento = obtener_informe(informe["id"])
                    self.assertGreater(documento["palabras"], 0)
                    self.assertGreater(len(documento["encabezados"]), 0)
                    self.assertTrue(documento["contenido"].startswith("#"))

    def test_identificadores_no_registrados_no_exponen_el_sistema_de_archivos(self):
        with self.assertRaises(KeyError):
            obtener_codigo("../../etc/passwd")
        with self.assertRaises(KeyError):
            obtener_informe("../../README")


class TrazasConCodigoRealTests(unittest.TestCase):
    def test_cada_traza_pertenece_a_su_funcion_real(self):
        casos = {
            "a_estrella": ("a-estrella", "a_estrella"),
            "dijkstra": ("no-informada", "dijkstra"),
            "bfs": ("no-informada", "bfs"),
        }

        for algoritmo, (archivo_id, funcion) in casos.items():
            with self.subTest(algoritmo=algoritmo):
                _, lineas = fragmento_traza(algoritmo)
                documento = obtener_codigo(archivo_id)
                bloque = next(item for item in documento["outline"] if item["nombre"] == funcion)
                self.assertTrue(all(bloque["linea"] <= item["linea"] <= bloque["fin"] for item in lineas))
                self.assertEqual([item["linea"] for item in lineas], sorted(item["linea"] for item in lineas))
                for item in lineas:
                    original = documento["lineas"][item["linea"] - 1]
                    self.assertEqual(item["codigo"], original["codigo"].strip())


if __name__ == "__main__":
    unittest.main()
