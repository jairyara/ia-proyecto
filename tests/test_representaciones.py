"""Pruebas de Semana 07: Amazon, reglas y autómata POD."""

from __future__ import annotations

import unittest
from contextlib import redirect_stdout
from io import StringIO

from src.representaciones.automata import validar_entrega
from src.representaciones.numerica import (
    VectorParada,
    calcular_estadisticas,
    cargar_dataset,
    evaluar_vector,
    perfiles_demostracion,
)
from src.representaciones.reconocimiento import contexto_dataset, evaluar_parada
from src.representaciones_reconocimiento import ejecutar_representaciones, mostrar_resultados
from src.representaciones.simbolica import (
    construir_umbrales,
    describir_hecho,
    evaluar_reglas,
    vector_a_hechos,
)


class DatosAmazonTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.datos = cargar_dataset()
        cls.estadisticas = calcular_estadisticas(cls.datos)

    def test_usa_14411_registros_reales_sin_nulos(self):
        self.assertEqual(len(self.datos), 14411)
        self.assertEqual(self.estadisticas["total_registros"], 14411)
        self.assertEqual(self.estadisticas["mediana"], [14.9, 0.0095, 56.0])
        self.assertEqual(self.estadisticas["q3"], [20.4655, 0.0213, 85.0])
        for obtenido, esperado in zip(self.estadisticas["iqr"], [11.0995, 0.0177, 45.8]):
            self.assertAlmostEqual(obtenido, esperado, places=6)

    def test_referencia_tiene_distancia_cero(self):
        referencia = VectorParada(*self.estadisticas["mediana"])
        resultado = evaluar_vector(referencia, self.estadisticas)
        self.assertEqual(resultado["distancia_cruda"], 0.0)
        self.assertEqual(resultado["distancia_normalizada"], 0.0)

    def test_perfiles_seleccionados_son_deterministas(self):
        perfiles = perfiles_demostracion(self.datos, self.estadisticas)
        self.assertEqual(
            [item["pedido_id"] for item in perfiles],
            ["AMZ-06380", "AMZ-05429", "AMZ-05050", "AMZ-06618", "AMZ-00150"],
        )


class RepresentacionSimbolicaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.estadisticas = calcular_estadisticas(cargar_dataset())
        cls.umbrales = construir_umbrales(cls.estadisticas)

    def test_limite_es_estricto_y_superarlo_activa_hechos(self):
        en_limite = VectorParada(*self.estadisticas["q3"])
        self.assertEqual(vector_a_hechos(en_limite, self.umbrales), [])

        superior = VectorParada(
            self.estadisticas["q3"][0] + 0.001,
            self.estadisticas["q3"][1] + 0.0001,
            self.estadisticas["q3"][2] + 0.1,
        )
        hechos = vector_a_hechos(superior, self.umbrales)
        self.assertEqual(
            [item["hecho"] for item in hechos],
            ["parada_lejana", "volumen_alto", "servicio_prolongado"],
        )

    def test_reglas_explican_activaciones_y_faltantes(self):
        resultado = evaluar_reglas(["parada_lejana", "servicio_prolongado"])
        self.assertEqual([item["accion"] for item in resultado["activadas"]], ["riesgo_desviacion_operativa"])
        self.assertEqual(len(resultado["parciales"]), 2)
        self.assertIn("volumen_alto", resultado["parciales"][0]["faltantes"])

    def test_traduccion_inversa_cita_percentil(self):
        detalle = describir_hecho("volumen_alto", self.umbrales)
        self.assertEqual(detalle["campo"], "volumen_total_m3")
        self.assertEqual(detalle["limite"], 0.0213)
        self.assertEqual(detalle["origen"], "percentil_75_amazon")


class AutomataPodTests(unittest.TestCase):
    def test_casos_controlados(self):
        esperado = {"AVF": ("q3", True), "AVC": ("q_fallo", False), "AF": ("q_fallo", False), "AV": ("q2", False)}
        for secuencia, (estado, aceptada) in esperado.items():
            with self.subTest(secuencia=secuencia):
                resultado = validar_entrega(secuencia)
                self.assertEqual(resultado["estado_final"], estado)
                self.assertEqual(resultado["aceptada"], aceptada)

    def test_fallo_es_absorbente_y_vacia_se_rechaza(self):
        self.assertEqual(validar_entrega("AFCVA")["estado_final"], "q_fallo")
        self.assertFalse(validar_entrega("")["aceptada"])


class IntegracionRepresentacionesTests(unittest.TestCase):
    def test_contexto_conserva_cantidades_y_procedencia(self):
        contexto = contexto_dataset()
        self.assertEqual(contexto["fuente"]["total_registros"], 14411)
        self.assertEqual(contexto["fuente"]["rutas"], 100)
        self.assertEqual(
            sum(item["registros"] for item in contexto["distribucion_hechos"]),
            14411,
        )
        self.assertEqual(len(contexto["perfiles"]), 5)

    def test_evaluacion_vincula_las_tres_representaciones(self):
        resultado = evaluar_parada("AMZ-00150", "AVF")
        self.assertEqual(resultado["pedido"]["pedido_id"], "AMZ-00150")
        self.assertEqual(len(resultado["simbolica"]["hechos"]), 3)
        self.assertEqual(len(resultado["simbolica"]["reglas_activadas"]), 3)
        self.assertTrue(resultado["automata_pod"]["aceptada"])
        self.assertIn("amazon_pedidos.csv", resultado["procedencia"]["vector"])

    def test_script_muestra_las_tres_representaciones(self):
        salida = StringIO()
        with redirect_stdout(salida):
            mostrar_resultados(ejecutar_representaciones())

        texto = salida.getvalue()
        self.assertIn("Representación numérica", texto)
        self.assertIn("Representación simbólica", texto)
        self.assertIn("Autómata POD", texto)
        self.assertIn("AVF: aceptada", texto)


if __name__ == "__main__":
    unittest.main()
