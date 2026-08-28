"""Pruebas unitarias para los algoritmos de búsqueda, heurísticas y replanificación."""

from __future__ import annotations

import json
from pathlib import Path
import unittest

from src.busqueda.a_estrella import (
    a_estrella,
    heuristica_haversine_km,
    heuristica_haversine_segundos,
    heuristica_manhattan,
)
from src.busqueda.grafo import GrafoEntregas, Parada
from src.busqueda.no_informada import bfs, dijkstra
from src.busqueda.replanificacion import replanificar_ruta

GRID_TEST = [
    ".....",
    ".###.",
    "...#.",
    ".#...",
    ".....",
]


class GrafoTests(unittest.TestCase):
    """Pruebas para la estructura de datos del grafo."""

    def test_creacion_y_vecinos(self):
        grafo = GrafoEntregas()
        grafo.agregar_nodo(Parada(stop_id="A", lat=1.0, lng=1.0))
        grafo.agregar_nodo(Parada(stop_id="B", lat=1.1, lng=1.1))
        grafo.agregar_arista("A", "B", 10.5)

        vecinos = grafo.vecinos("A")
        self.assertEqual(len(vecinos), 1)
        self.assertEqual(vecinos[0], ("B", 10.5))

    def test_bloqueo_y_desbloqueo_aristas(self):
        grafo = GrafoEntregas()
        grafo.agregar_arista("A", "B", 5.0)
        self.assertFalse(grafo.esta_bloqueada("A", "B"))
        self.assertEqual(grafo.costo_arista("A", "B"), 5.0)

        grafo.bloquear_arista("A", "B")
        self.assertTrue(grafo.esta_bloqueada("A", "B"))
        self.assertIsNone(grafo.costo_arista("A", "B"))
        self.assertEqual(len(grafo.vecinos("A")), 0)

        grafo.desbloquear_arista("A", "B")
        self.assertFalse(grafo.esta_bloqueada("A", "B"))
        self.assertEqual(len(grafo.vecinos("A")), 1)


class HeuristicaTests(unittest.TestCase):
    """Pruebas para las funciones heurísticas."""

    def test_heuristica_manhattan(self):
        p1 = Parada(stop_id="(0,0)", lat=0.0, lng=0.0)
        p2 = Parada(stop_id="(4,4)", lat=4.0, lng=4.0)
        h_val = heuristica_manhattan(p1, p2)
        self.assertEqual(h_val, 8.0)

    def test_heuristica_haversine_admisible(self):
        # Dos paradas reales en Chicago/Illinois
        p1 = Parada(stop_id="P1", lat=42.129, lng=-88.027)
        p2 = Parada(stop_id="P2", lat=42.133, lng=-88.043)

        h_seg = heuristica_haversine_segundos(p1, p2, v_max_kmh=80.0)
        self.assertGreater(h_seg, 0.0)

        # Misma parada -> h = 0
        self.assertEqual(heuristica_haversine_segundos(p1, p1), 0.0)
        self.assertEqual(heuristica_haversine_km(p1, p1), 0.0)


class BusquedaCuadriculaTests(unittest.TestCase):
    """Pruebas del caso de control en cuadrícula (Semana 4 guía)."""

    def setUp(self):
        self.grafo = GrafoEntregas.desde_cuadricula(GRID_TEST)

    def test_astar_encuentra_costo_optimo_ocho(self):
        res = a_estrella(self.grafo, "(0,0)", "(4,4)", fn_heuristica=heuristica_manhattan)
        self.assertTrue(res.encontrado)
        self.assertEqual(res.costo_total, 8.0)
        self.assertEqual(res.ruta[0], "(0,0)")
        self.assertEqual(res.ruta[-1], "(4,4)")

    def test_dijkstra_y_astar_mismo_costo(self):
        res_a = a_estrella(self.grafo, "(0,0)", "(4,4)", fn_heuristica=heuristica_manhattan)
        res_d = dijkstra(self.grafo, "(0,0)", "(4,4)")
        res_b = bfs(self.grafo, "(0,0)", "(4,4)")

        self.assertEqual(res_a.costo_total, res_d.costo_total)
        self.assertEqual(res_a.costo_total, res_b.costo_total)
        # A* debe expandir menos o iguales nodos que Dijkstra
        self.assertLessEqual(res_a.nodos_expandidos, res_d.nodos_expandidos)

    def test_destino_inalcanzable(self):
        # Bloquear todos los caminos hacia (4,4)
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nr, nc = 4 + dr, 4 + dc
            if 0 <= nr < 5 and 0 <= nc < 5:
                self.grafo.bloquear_arista(f"({nr},{nc})", "(4,4)")

        res = a_estrella(self.grafo, "(0,0)", "(4,4)")
        self.assertFalse(res.encontrado)
        self.assertEqual(res.ruta, [])


class BusquedaAmazonTests(unittest.TestCase):
    """Pruebas sobre los grafos de datos reales de Amazon Last Mile."""

    @classmethod
    def setUpClass(cls):
        cls.ruta_json = Path(__file__).resolve().parent.parent / "data" / "amazon_rutas_muestra.json"
        if cls.ruta_json.exists():
            with open(cls.ruta_json, "r", encoding="utf-8") as f:
                cls.datos = json.load(f)
        else:
            cls.datos = {}

    def test_carga_grafo_amazon(self):
        if not self.datos:
            self.skipTest("Dataset amazon_rutas_muestra.json no encontrado.")

        r_id = list(self.datos.keys())[0]
        grafo = GrafoEntregas.desde_amazon_ruta(self.datos[r_id])

        self.assertGreater(len(grafo.nodos), 10)
        self.assertGreater(len(grafo.aristas), 10)

    def test_optimalidad_astar_vs_dijkstra_en_amazon(self):
        if not self.datos:
            self.skipTest("Dataset amazon_rutas_muestra.json no encontrado.")

        r_id = list(self.datos.keys())[0]
        r_data = self.datos[r_id]
        grafo = GrafoEntregas.desde_amazon_ruta(r_data)
        depot = r_data["depot_stop_id"]
        paradas = [s["stop_id"] for s in r_data["stops"] if s["stop_id"] != depot]
        meta = paradas[5]

        res_a = a_estrella(grafo, depot, meta, v_max_kmh=80.0)
        res_d = dijkstra(grafo, depot, meta)

        self.assertTrue(res_a.encontrado)
        self.assertTrue(res_d.encontrado)
        # Optimalidad: costos iguales
        self.assertAlmostEqual(res_a.costo_total, res_d.costo_total, places=2)
        # Eficiencia: A* expande menos o igual cantidad de nodos
        self.assertLessEqual(res_a.nodos_expandidos, res_d.nodos_expandidos)


class ReplanificacionTests(unittest.TestCase):
    """Pruebas del ciclo dinámico de replanificación."""

    def test_replanificacion_en_cuadricula(self):
        grafo = GrafoEntregas.desde_cuadricula(GRID_TEST)
        res_ini = a_estrella(grafo, "(0,0)", "(4,4)", fn_heuristica=heuristica_manhattan)
        self.assertTrue(res_ini.encontrado)

        # Simular bloqueo en la segunda arista
        res_rep = replanificar_ruta(
            grafo=grafo,
            ruta_planificada=res_ini.ruta,
            paso_bloqueo=1,
            fn_heuristica=heuristica_manhattan,
        )

        self.assertTrue(res_rep.replanificacion_exitosa)
        self.assertNotEqual(res_rep.nueva_subruta, [])
        self.assertEqual(res_rep.ruta_completa_ejecutada[-1], "(4,4)")
        self.assertEqual(res_rep.ruta_completa_ejecutada[0], "(0,0)")


if __name__ == "__main__":
    unittest.main()
