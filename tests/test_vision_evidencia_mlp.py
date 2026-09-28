"""Registro real del MLP en PostgreSQL, siempre en schema de prueba aislado."""

import os
from tempfile import TemporaryDirectory
import unittest
from pathlib import Path
from unittest.mock import patch

from alembic import command
from fastapi.testclient import TestClient
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from src.datos.importacion import importar_amazon
from src.persistencia.modelo_visual import ModeloVisual, MuestraModeloVisual
from src.vision.evidencia_mlp import registrar_modelo
from src.vision.manifiesto import ErrorVisual
from src.vision.modelo_mlp import entrenar_y_evaluar, guardar_resultado
from src.vision.particion import preparar_piloto
from api.main import app
from tests.test_migraciones import PostgreSQLAislado
from tests.test_persistencia_visual import FixturesVisuales


@unittest.skipUnless(os.getenv("TEST_DATABASE_URL"), "Requiere TEST_DATABASE_URL")
class EvidenciaMLPTests(FixturesVisuales, PostgreSQLAislado):
    def setUp(self):
        super().setUp()
        self.migrar(command.upgrade, "head")
        self.preparar()
        importar_amazon(self.csv, self.amazon, motor=self.motor)
        self.seed()
        self.particion = preparar_piloto(self.originales, self.manifiesto)
        self.resultado = entrenar_y_evaluar(self.particion)
        temporal = TemporaryDirectory()
        self.addCleanup(temporal.cleanup)
        self.artefacto = Path(temporal.name) / "semana08" / "modelo_mlp_logistica.pkl"
        self.meta = guardar_resultado(self.resultado, self.artefacto.parent)

    def test_registro_idempotente_y_particion_completa(self):
        with Session(self.motor) as sesion, sesion.begin():
            modelo, nuevo = registrar_modelo(sesion, self.particion, self.meta, self.artefacto)
            self.assertTrue(nuevo)
            self.assertGreater(modelo.dataset_id, 0)
        with Session(self.motor) as sesion, sesion.begin():
            _, nuevo = registrar_modelo(sesion, self.particion, self.meta, self.artefacto)
            self.assertFalse(nuevo)
            filas = sesion.scalars(select(MuestraModeloVisual)).all()
            self.assertEqual(len(filas), 200)
            self.assertEqual(sum(f.split == "test" and f.clase_predicha is not None for f in filas), 50)
            self.assertEqual(sesion.scalar(select(func.count()).select_from(ModeloVisual)), 1)

    def test_rechaza_artefacto_alterado_sin_escribir(self):
        self.artefacto.write_bytes(b"alterado")
        with Session(self.motor) as sesion, sesion.begin(), self.assertRaises(ErrorVisual):
            registrar_modelo(sesion, self.particion, self.meta, self.artefacto)
        with Session(self.motor) as sesion:
            self.assertEqual(sesion.scalar(select(func.count()).select_from(ModeloVisual)), 0)

    def test_api_documentada_lee_metricas_predicciones_y_ontologia(self):
        with Session(self.motor) as sesion, sesion.begin():
            registrar_modelo(sesion, self.particion, self.meta, self.artefacto)
        with patch.dict(os.environ, {"DATABASE_URL": self.motor.url.render_as_string(hide_password=False)}):
            with TestClient(app) as cliente:
                resumen = cliente.get("/api/modelo-visual/resumen")
                self.assertEqual(resumen.status_code, 200)
                self.assertEqual(resumen.json()["total_test"], 50)
                pagina = cliente.get("/api/modelo-visual/predicciones?limite=5")
                self.assertEqual(pagina.status_code, 200)
                self.assertEqual(pagina.json()["total"], 50)
                self.assertEqual(len(pagina.json()["items"]), 5)
                grafo = cliente.get("/api/modelo-visual/ontologia")
                self.assertEqual(grafo.status_code, 200)
                self.assertEqual(len(grafo.json()["relaciones"]), 13)
                imagen_id = pagina.json()["items"][1]["imagen_id"]
                grafo_elegido = cliente.get(f"/api/modelo-visual/ontologia?imagen_id={imagen_id}")
                self.assertEqual(grafo_elegido.status_code, 200)
                self.assertEqual(grafo_elegido.json()["ejemplo_imagen_id"], imagen_id)
                self.assertEqual(cliente.get("/api/modelo-visual/ontologia?imagen_id=999999").status_code, 404)
                rutas = cliente.get("/openapi.json").json()["paths"]
                self.assertIn("/api/modelo-visual/resumen", rutas)
