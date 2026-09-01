"""Pruebas de integración entre dashboard y módulos académicos."""

from __future__ import annotations

import unittest

from api.schemas.busqueda_dto import ReplanificacionRequest, SimulacionBusquedaRequest
from api.schemas.clasificacion_dto import RequerimientoRequest
from api.schemas.modelado_dto import PedidoRequest
from api.services.busqueda import replanificar_busqueda, simular_busqueda
from api.services.clasificacion import evaluar_requerimiento
from api.services.modelado import obtener_metricas, predecir_riesgo


class DashboardBusquedaTests(unittest.TestCase):
    def test_traza_astar_conserva_el_resultado_canonico(self):
        respuesta = simular_busqueda(SimulacionBusquedaRequest())

        self.assertTrue(respuesta["resultado"]["encontrado"])
        self.assertEqual(respuesta["resultado"]["costo_total"], 8.0)
        self.assertEqual(respuesta["resultado"]["ruta"][0], "(0,0)")
        self.assertEqual(respuesta["resultado"]["ruta"][-1], "(4,4)")
        self.assertEqual(respuesta["pasos"][0]["evento"], "init")
        self.assertEqual(respuesta["pasos"][-1]["evento"], "path")

    def test_dijkstra_no_usa_heuristica_en_la_traza(self):
        solicitud = SimulacionBusquedaRequest(algoritmo="dijkstra")
        respuesta = simular_busqueda(solicitud)
        self.assertTrue(all(paso["h"] == 0.0 for paso in respuesta["pasos"]))

    def test_replanificacion_bloquea_tramo_y_encuentra_alternativa(self):
        solicitud = SimulacionBusquedaRequest()
        inicial = simular_busqueda(solicitud)
        evento = ReplanificacionRequest(
            simulacion=solicitud,
            ruta_original=inicial["resultado"]["ruta"],
            paso_bloqueo=1,
        )
        respuesta = replanificar_busqueda(evento)

        self.assertTrue(respuesta["replanificacion"]["replanificacion_exitosa"])
        self.assertTrue(respuesta["simulacion"]["resultado"]["encontrado"])
        self.assertEqual(
            len(respuesta["simulacion"]["aristas_bloqueadas"]), 1
        )


class DashboardModeladoTests(unittest.TestCase):
    def test_prediccion_devuelve_probabilidad_y_factores(self):
        pedido = PedidoRequest(
            distancia_km=18,
            volumen_m3=0.3,
            prioridad="alta",
            ventana_min=60,
            cadena_frio=1,
            hora_pico=1,
            zona_rural=0,
            trafico_index=0.8,
        )
        respuesta = predecir_riesgo(pedido)
        self.assertGreaterEqual(respuesta["probabilidad"], 0.0)
        self.assertLessEqual(respuesta["probabilidad"], 1.0)
        self.assertIn(respuesta["etiqueta"], (0, 1))
        self.assertGreater(len(respuesta["factores"]), 0)
        self.assertIn("resultados", obtener_metricas())


class DashboardClasificacionTests(unittest.TestCase):
    def test_clasificacion_conserva_evidencia_multi_area(self):
        respuesta = evaluar_requerimiento(
            RequerimientoRequest(
                descripcion="Calcular una ruta A* y validar restricciones de ventana horaria"
            )
        )
        self.assertEqual(respuesta["principal"], "Búsqueda y optimización")
        self.assertGreaterEqual(len(respuesta["detectadas"]), 2)
        self.assertIn("a estrella", respuesta["evidencia"][0]["palabras"])


if __name__ == "__main__":
    unittest.main()
