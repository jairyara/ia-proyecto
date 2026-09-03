"""Pruebas del sistema híbrido de trazabilidad (Semana 5)."""

from __future__ import annotations

import unittest

from src.hibrido.sistema import (
    CONSULTAS_EJEMPLO,
    DOCS,
    MIN_DOCUMENTOS,
    RULES,
    TRAIN_X,
    TRAIN_Y,
    answer,
    clasificar,
    evaluar_reglas,
    load_documents,
    recuperar_evidencia,
)


class BaseConocimientoTests(unittest.TestCase):
    def test_base_tiene_al_menos_ocho_protocolos(self):
        documentos = load_documents()

        self.assertGreaterEqual(len(documentos), MIN_DOCUMENTOS)
        self.assertTrue(all(documento.strip() for documento in documentos))


class ReglasExpertasTests(unittest.TestCase):
    def test_existen_cinco_reglas_del_dominio_logistico(self):
        self.assertEqual(len(RULES), 5)
        for regla in RULES:
            with self.subTest(regla=regla.accion):
                self.assertTrue(regla.palabras)
                self.assertTrue(regla.descripcion)

    def test_regla_cadena_frio_reporta_la_palabra_detonante(self):
        activadas = evaluar_reglas("El furgón perdió temperatura en ruta")

        self.assertEqual([item["accion"] for item in activadas], ["activar_protocolo_cadena_frio"])
        self.assertIn("temperatura", activadas[0]["detonantes"])

    def test_consulta_sin_palabras_clave_no_dispara_reglas(self):
        self.assertEqual(evaluar_reglas("todo en orden durante la jornada"), [])

    def test_normalizacion_tolera_tildes_y_mayusculas(self):
        activadas = evaluar_reglas("CONGESTIÓN total en la autopista")

        self.assertEqual([item["accion"] for item in activadas], ["replanificar_ruta_alterna"])


class RecuperacionTests(unittest.TestCase):
    def test_recupera_protocolo_afin_con_similitud_en_rango(self):
        evidencia = recuperar_evidencia("cierres viales y accidentes de tránsito con bloqueos")

        self.assertIn("Protocolo 2", evidencia["documento"])
        self.assertGreaterEqual(evidencia["similitud"], 0.0)
        self.assertLessEqual(evidencia["similitud"], 1.0)


class ClasificacionTests(unittest.TestCase):
    def test_dataset_balanceado_en_cuatro_clases(self):
        self.assertEqual(len(TRAIN_X), 16)
        self.assertEqual(len(TRAIN_X), len(TRAIN_Y))
        conteo = {clase: TRAIN_Y.count(clase) for clase in set(TRAIN_Y)}
        self.assertTrue(all(cantidad == 4 for cantidad in conteo.values()))

    def test_probabilidades_suman_uno_y_estan_ordenadas(self):
        resultado = clasificar("sobrecupo de kilos en el camión")

        self.assertEqual(resultado["clase"], "capacidad_flota")
        total = sum(item["probabilidad"] for item in resultado["probabilidades"])
        self.assertAlmostEqual(total, 1.0, places=5)
        valores = [item["probabilidad"] for item in resultado["probabilidades"]]
        self.assertEqual(valores, sorted(valores, reverse=True))


class RespuestaHibridaTests(unittest.TestCase):
    def test_consultas_de_la_guia_producen_la_traza_esperada(self):
        esperado = {
            "cadena_frio": "activar_protocolo_cadena_frio",
            "rutas_trafico": "replanificar_ruta_alterna",
            "capacidad_flota": "reasignar_vehiculo_mayor_capacidad",
        }

        for consulta in CONSULTAS_EJEMPLO:
            with self.subTest(consulta=consulta):
                resultado = answer(consulta)
                self.assertIn(resultado["clase"], esperado)
                self.assertIn(esperado[resultado["clase"]], resultado["reglas"])
                self.assertTrue(resultado["evidencia"])
                self.assertGreater(resultado["similitud"], 0.0)

    def test_la_respuesta_conserva_trazabilidad_completa(self):
        resultado = answer(CONSULTAS_EJEMPLO[0])

        self.assertEqual(resultado["consulta"], CONSULTAS_EJEMPLO[0])
        self.assertEqual(resultado["reglas_detalle"][0]["accion"], resultado["reglas"][0])
        self.assertEqual(resultado["clases"][0]["clase"], resultado["clase"])
        self.assertIn(resultado["evidencia"], DOCS)


if __name__ == "__main__":
    unittest.main()
