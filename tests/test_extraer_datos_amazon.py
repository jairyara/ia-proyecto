"""Pruebas unitarias para la extracción y curaduría del dataset Amazon Last Mile."""

from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

import pandas as pd

from src.extraer_datos_amazon import (
    construir_grafos_muestra,
    haversine_km,
    procesar_paradas_a_dataframe,
    render_reporte_datos,
    seleccionar_rutas_estratificadas,
)


class HaversineTests(unittest.TestCase):
    def test_distancia_cero_mismo_punto(self) -> None:
        dist = haversine_km(40.7128, -74.0060, 40.7128, -74.0060)
        self.assertAlmostEqual(dist, 0.0, places=5)

    def test_distancia_conocida_coherente(self) -> None:
        # Distancia aproximada entre Chicago y Los Ángeles ~2800 km
        dist = haversine_km(41.8781, -87.6298, 34.0522, -118.2437)
        self.assertGreater(dist, 2700.0)
        self.assertLess(dist, 3000.0)


class SeleccionRutasTests(unittest.TestCase):
    def setUp(self) -> None:
        self.rutas_mock = {
            f"Ruta_{i}": {"station_code": f"EST_{(i % 4) + 1}"}
            for i in range(20)
        }

    def test_cantidad_exacta(self) -> None:
        seleccionadas = seleccionar_rutas_estratificadas(self.rutas_mock, num_routes=8, seed=42)
        self.assertEqual(len(seleccionadas), 8)

    def test_cobertura_estratificada(self) -> None:
        seleccionadas = seleccionar_rutas_estratificadas(self.rutas_mock, num_routes=8, seed=42)
        estaciones_cubiertas = {
            self.rutas_mock[r]["station_code"] for r in seleccionadas
        }
        self.assertEqual(len(estaciones_cubiertas), 4)

    def test_reproducibilidad_con_seed(self) -> None:
        sel1 = seleccionar_rutas_estratificadas(self.rutas_mock, num_routes=5, seed=1234)
        sel2 = seleccionar_rutas_estratificadas(self.rutas_mock, num_routes=5, seed=1234)
        self.assertEqual(sel1, sel2)


class ProcesamientoParadasTests(unittest.TestCase):
    def setUp(self) -> None:
        self.routes_mock = {
            "R1": {
                "station_code": "DCH4",
                "date_YYYY_MM_DD": "2026-08-28",
                "departure_time_utc": "08:00:00",
                "executor_capacity_cm3": 4000000.0,
                "stops": {
                    "ST0": {"type": "Station", "lat": 41.88, "lng": -87.63, "zone_id": "D-1"},
                    "P1": {"type": "Dropoff", "lat": 41.90, "lng": -87.65, "zone_id": "D-2"},
                    "P2": {"type": "Dropoff", "lat": 41.92, "lng": -87.68, "zone_id": float("nan")},
                },
            }
        }
        self.sequences_mock = {"R1": {"actual": {"ST0": 0, "P1": 1, "P2": 2}}}
        self.packages_mock = {
            "R1": {
                "ST0": {},
                "P1": {
                    "PKG1": {
                        "dimensions": {"depth_cm": 20.0, "height_cm": 10.0, "width_cm": 10.0},
                        "planned_service_time_seconds": 60.0,
                        "time_window": {"start_time_utc": "2026-08-28 09:00:00", "end_time_utc": "2026-08-28 11:00:00"},
                    }
                },
                "P2": {
                    "PKG2": {
                        "dimensions": {"depth_cm": 30.0, "height_cm": 20.0, "width_cm": 10.0},
                        "planned_service_time_seconds": 120.0,
                        "time_window": {"start_time_utc": float("nan"), "end_time_utc": float("nan")},
                    }
                },
            }
        }

    def test_dataframe_limpio_y_columnas(self) -> None:
        df = procesar_paradas_a_dataframe(
            self.routes_mock, self.sequences_mock, self.packages_mock, ["R1"]
        )
        self.assertEqual(len(df), 3)
        columnas_esperadas = {
            "pedido_id",
            "route_id",
            "stop_id",
            "station_code",
            "fecha",
            "hora_salida_utc",
            "tipo_parada",
            "lat",
            "lng",
            "zone_id",
            "distancia_deposito_km",
            "num_paquetes",
            "volumen_total_m3",
            "volumen_promedio_m3",
            "tiempo_servicio_seg",
            "tiene_ventana_horaria",
            "duracion_ventana_min",
            "secuencia_real",
            "capacidad_vehiculo_m3",
            "retrasado_estimado",
        }
        self.assertTrue(columnas_esperadas.issubset(set(df.columns)))

    def test_tratamiento_nan_y_ventanas(self) -> None:
        df = procesar_paradas_a_dataframe(
            self.routes_mock, self.sequences_mock, self.packages_mock, ["R1"]
        )
        # P2 tenía zone_id NaN -> debe ser 'SIN_ZONA'
        fila_p2 = df[df["stop_id"] == "P2"].iloc[0]
        self.assertEqual(fila_p2["zone_id"], "SIN_ZONA")
        self.assertEqual(fila_p2["tiene_ventana_horaria"], 0)

        # P1 tenía ventana de 2 horas (120 min)
        fila_p1 = df[df["stop_id"] == "P1"].iloc[0]
        self.assertEqual(fila_p1["tiene_ventana_horaria"], 1)
        self.assertEqual(fila_p1["duracion_ventana_min"], 120.0)


class GrafosMuestraTests(unittest.TestCase):
    def test_construccion_grafo(self) -> None:
        sample_routes = {
            "R1": {
                "station_code": "DLA3",
                "executor_capacity_cm3": 3000000.0,
                "stops": {
                    "DEP": {"type": "Station", "lat": 34.0, "lng": -118.0, "zone_id": "Z1"},
                    "ST1": {"type": "Dropoff", "lat": 34.1, "lng": -118.1, "zone_id": "Z2"},
                },
            }
        }
        sample_pkgs = {"R1": {"ST1": {"P1": {"dimensions": {"depth_cm": 10, "height_cm": 10, "width_cm": 10}}}}}
        sample_travel = {"R1": {"DEP": {"DEP": 0.0, "ST1": 150.0}, "ST1": {"DEP": 150.0, "ST1": 0.0}}}
        sample_seq = {"R1": {"actual": {"DEP": 0, "ST1": 1}}}

        grafos = construir_grafos_muestra(sample_routes, sample_pkgs, sample_travel, sample_seq)
        self.assertIn("R1", grafos)
        self.assertEqual(grafos["R1"]["depot_stop_id"], "DEP")
        self.assertEqual(grafos["R1"]["num_paradas"], 2)
        self.assertIn("travel_times_seg", grafos["R1"])


class ReportePersistenciaTests(unittest.TestCase):
    def test_generacion_reporte(self) -> None:
        df = pd.DataFrame(
            [
                {
                    "pedido_id": "AMZ-001",
                    "station_code": "DCH4",
                    "stop_id": "P1",
                    "distancia_deposito_km": 5.0,
                    "num_paquetes": 2,
                    "volumen_total_m3": 0.02,
                    "tiempo_servicio_seg": 60.0,
                    "retrasado_estimado": 0,
                }
            ]
        )
        reporte = render_reporte_datos(
            df,
            num_rutas=1,
            num_grafos=1,
            ruta_csv=Path("data/test.csv"),
            ruta_grafo=Path("data/test.json"),
        )
        self.assertIn("# Dataset Amazon Last Mile Routing Challenge", reporte)
        self.assertIn("DCH4", reporte)
        self.assertIn("distancia_deposito_km", reporte)


if __name__ == "__main__":
    unittest.main()
