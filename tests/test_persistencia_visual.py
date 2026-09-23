"""Fase 4: fixtures propias, almacenamiento real y PostgreSQL optativo aislado."""

from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
import csv
from dataclasses import replace
from hashlib import sha256
from io import StringIO
import json
import os
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from alembic import command
from sqlalchemy import event, func, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.datos.importacion import importar_amazon
from src.datos.validacion import COLUMNAS, ManifiestoAmazon
from src.persistencia.imagenes import AsociacionVisual, Imagen, PilotoVisual
from src.persistencia.modelos import Dataset, Importacion
from src.vision.almacenamiento import publicar_lote, resolver_clave
from src.vision.asociacion import construir_mapa, hash_mapa
from src.vision.importacion import ErrorImportacionVisual, importar_piloto
from src.vision.manifiesto import ErrorVisual, auditar_piloto, json_bytes
from test_migraciones import PostgreSQLAislado
from test_piloto_visual import png


class FixturesVisuales:
    def preparar(self):
        temporal = TemporaryDirectory()
        self.addCleanup(temporal.cleanup)
        self.base = Path(temporal.name).resolve()
        self.originales = self.base / "originales"
        self.almacen = self.base / "almacen"
        self.manifiesto = self.base / "visual.json"
        self.csv = self.base / "amazon.csv"
        inventario = []
        for i in range(200):
            ruta = f"{'damaged' if i < 100 else 'intact'}/side/{i:013d}_side.png"
            contenido = png(color=(i, 30, 40))
            destino = self.originales / ruta
            destino.parent.mkdir(parents=True, exist_ok=True)
            destino.write_bytes(contenido)
            inventario.append({"ruta": ruta, "bytes": len(contenido)})
        parche = patch("src.vision.manifiesto.cargar_fuente", return_value=({}, inventario))
        parche.start()
        self.addCleanup(parche.stop)
        self.visual = auditar_piloto(self.originales)
        self.manifiesto.write_bytes(json_bytes(self.visual))
        fuente = Path(__file__).parent / "fixtures/amazon_minimo.csv"
        filas = list(csv.DictReader(StringIO(fuente.read_text())))
        salida = StringIO(newline="")
        escritor = csv.DictWriter(salida, fieldnames=COLUMNAS)
        escritor.writeheader()
        for i in range(240):
            escritor.writerow({**filas[i % 4], "pedido_id": f"FIX-{i:05d}", "stop_id": f"STOP-{i:05d}"})
        self.csv.write_bytes(salida.getvalue().encode())
        self.amazon = ManifiestoAmazon("amazon-logistica", "fixture-v1", sha256(self.csv.read_bytes()).hexdigest(),
                                      "Fixture propia para asociaciones.", 240, 2, 2)
        self.mapa = construir_mapa(self.csv.read_bytes(), self.amazon, self.visual, self.manifiesto.read_bytes())
        self.lote = hash_mapa(self.mapa)

    def seed(self, **kwargs):
        return importar_piloto(self.originales, self.manifiesto, self.csv, self.amazon,
                              self.almacen, motor=getattr(self, "motor", None), **kwargs)


class VisualOfflineTests(FixturesVisuales, unittest.TestCase):
    def setUp(self):
        self.preparar()

    def test_mapa_reproducible_200_unicos_y_orden_independiente(self):
        invertido = deepcopy(self.visual)
        invertido["imagenes"].reverse()
        nuevo = construir_mapa(self.csv.read_bytes(), self.amazon, invertido, self.manifiesto.read_bytes())
        self.assertEqual(nuevo, self.mapa)
        pares = nuevo["asociaciones"]
        self.assertEqual(len({a["pedido_id"] for a in pares}), 200)
        self.assertEqual(len({a["imagen_id_origen"] for a in pares}), 200)
        self.assertEqual({a["tipo_asociacion"] for a in pares}, {"simulada"})
        self.assertNotEqual(nuevo["semilla_paradas"], nuevo["semilla_imagenes"])

    def test_dry_run_no_conecta_ni_escribe(self):
        with patch("src.vision.importacion.Session", side_effect=AssertionError("No BD")):
            resultado = self.seed(dry_run=True)
        self.assertEqual(resultado["mapa_sha256"], self.lote)
        self.assertFalse(self.almacen.exists())

    def test_version_insegura_y_fuente_alterada(self):
        with self.assertRaises(ErrorVisual):
            self.seed(dry_run=True, version="../otro")
        self.csv.write_bytes(self.csv.read_bytes() + b"\n")
        with self.assertRaises(ErrorImportacionVisual):
            self.seed(dry_run=True)
        self.assertFalse(self.almacen.exists())

    def test_publicacion_reusa_sin_sobrescribir_y_rechaza_corrupcion(self):
        publicar_lote(self.almacen, self.originales, self.visual, self.mapa, self.lote)
        archivo = resolver_clave(self.almacen, f"{self.lote}/{self.visual['imagenes'][0]['sha256']}.png")
        antes = archivo.stat().st_mtime_ns
        publicar_lote(self.almacen, self.originales, self.visual, self.mapa, self.lote)
        self.assertEqual(antes, archivo.stat().st_mtime_ns)
        archivo.write_bytes(b"alterado")
        with self.assertRaises(ErrorVisual):
            publicar_lote(self.almacen, self.originales, self.visual, self.mapa, self.lote)
        self.assertEqual(archivo.read_bytes(), b"alterado")

    def test_fallo_copia_limpia_solo_staging_propio(self):
        self.almacen.mkdir()
        ajeno = self.almacen / "ajeno.txt"
        ajeno.write_text("conservar")
        from src.vision.almacenamiento import _escribir
        llamadas = 0
        def fallo(*args):
            nonlocal llamadas
            llamadas += 1
            if llamadas == 4:
                raise OSError("copia fallida")
            _escribir(*args)
        with patch("src.vision.almacenamiento._escribir", side_effect=fallo), self.assertRaises(OSError):
            publicar_lote(self.almacen, self.originales, self.visual, self.mapa, self.lote)
        self.assertEqual(list(self.almacen.iterdir()), [ajeno])
        publicar_lote(self.almacen, self.originales, self.visual, self.mapa, self.lote)

    def test_claves_y_symlinks_inseguros(self):
        for clave in ("../x", "/etc/passwd", "a/../x.png", "a" * 64 + "/../x"):
            with self.assertRaises(ErrorVisual):
                resolver_clave(self.almacen, clave)
        self.almacen.mkdir()
        (self.almacen / self.lote).symlink_to(self.originales, target_is_directory=True)
        with self.assertRaises(ErrorVisual):
            publicar_lote(self.almacen, self.originales, self.visual, self.mapa, self.lote)

    def test_original_cambiado_entre_auditoria_y_copia(self):
        (self.originales / self.visual["imagenes"][0]["archivo"]).write_bytes(b"roto")
        with self.assertRaises(ErrorVisual):
            publicar_lote(self.almacen, self.originales, self.visual, self.mapa, self.lote)
        self.assertFalse((self.almacen / self.lote).exists())


@unittest.skipUnless(os.getenv("TEST_DATABASE_URL"), "Requiere PostgreSQL desechable TEST_DATABASE_URL")
class VisualPostgreSQLTests(FixturesVisuales, PostgreSQLAislado):
    def setUp(self):
        super().setUp()
        self.migrar(command.upgrade, "head")
        self.preparar()
        importar_amazon(self.csv, self.amazon, motor=self.motor)

    def contar(self, modelo):
        with Session(self.motor) as sesion:
            return sesion.scalar(select(func.count()).select_from(modelo))

    def test_importacion_idempotente_y_mapa_exacto_en_bd(self):
        primero, segundo = self.seed(), self.seed()
        self.assertEqual((primero["estado"], segundo["estado"]), ("completada", "sin_cambios"))
        self.assertEqual(segundo["filas_insertadas"], 0)
        self.assertEqual([self.contar(m) for m in (Imagen, AsociacionVisual, PilotoVisual)], [200, 200, 1])
        with Session(self.motor) as sesion:
            piloto = sesion.scalar(select(PilotoVisual))
            self.assertEqual(piloto.mapa_json.encode(), (self.almacen / self.lote / "mapa.json").read_bytes())
            self.assertEqual(json.loads(piloto.mapa_json), self.mapa)
            self.assertEqual(piloto.mapa_sha256, self.lote)

    def test_concurrencia_sin_duplicados(self):
        with ThreadPoolExecutor(max_workers=2) as executor:
            resultados = list(executor.map(lambda _: self.seed(), range(2)))
        self.assertEqual({r["estado"] for r in resultados}, {"completada", "sin_cambios"})
        self.assertEqual(self.contar(AsociacionVisual), 200)

    def test_fallo_copia_revierte_bd_y_audita(self):
        with patch("src.vision.almacenamiento._escribir", side_effect=OSError("secreto")), self.assertRaises(ErrorImportacionVisual):
            self.seed()
        self.assertEqual(self.contar(Imagen), 0)
        self.assertEqual(self.contar(PilotoVisual), 0)
        with Session(self.motor) as sesion:
            intento = sesion.scalar(select(Importacion).where(Importacion.fuente == "piloto-visual"))
            self.assertEqual(intento.estado, "fallida")
            self.assertNotIn("secreto", intento.error)
        self.assertEqual(self.seed()["estado"], "completada")

    def test_fallo_commit_conserva_lote_y_reintenta(self):
        def fallo(sesion):
            if any(isinstance(o, Importacion) and o.fuente == "piloto-visual" and o.estado == "completada" for o in sesion.dirty):
                raise RuntimeError("commit simulado")
        event.listen(Session, "before_commit", fallo)
        try:
            with self.assertRaises(ErrorImportacionVisual):
                self.seed()
        finally:
            event.remove(Session, "before_commit", fallo)
        self.assertEqual(self.contar(Imagen), 0)
        self.assertTrue((self.almacen / self.lote / "mapa.json").is_file())
        with patch("src.vision.almacenamiento._escribir", side_effect=AssertionError("Reutilizar")):
            self.assertEqual(self.seed()["estado"], "completada")

    def test_manifiesto_alterado_auditado_y_no_publicado(self):
        cambiado = deepcopy(self.visual)
        cambiado["imagenes"][0]["etiqueta"] = "otra"
        self.manifiesto.write_bytes(json_bytes(cambiado))
        with self.assertRaises(ErrorVisual):
            self.seed()
        self.assertEqual(self.contar(Imagen), 0)
        self.assertFalse(self.almacen.exists())

    def test_reintento_rechaza_bd_o_archivo_alterado(self):
        self.seed()
        with Session(self.motor) as sesion, sesion.begin():
            sesion.execute(update(Imagen).values(grupo_origen="alterado"))
        with self.assertRaisesRegex(ErrorVisual, "Metadatos"):
            self.seed()

    def test_archivo_publicado_alterado_no_repara_ni_reasigna(self):
        self.seed()
        archivo = self.almacen / self.lote / f"{self.visual['imagenes'][0]['sha256']}.png"
        archivo.write_bytes(b"alterado")
        with self.assertRaisesRegex(ErrorVisual, "alterado"):
            self.seed()
        self.assertEqual(archivo.read_bytes(), b"alterado")
        self.assertEqual(self.contar(AsociacionVisual), 200)

    def test_amazon_sin_version_exacta_no_publica_archivos(self):
        self.amazon = replace(self.amazon, version="no-importada")
        with self.assertRaisesRegex(ErrorVisual, "Amazon"):
            self.seed()
        self.assertEqual(self.contar(Imagen), 0)
        self.assertFalse(self.almacen.exists())

    def test_otro_mapa_misma_version_no_sobrescribe(self):
        self.seed()
        original = (self.almacen / self.lote / "mapa.json").read_bytes()
        # Mismos metadatos JSON, otros bytes: cambia el hash fijado del origen.
        self.manifiesto.write_bytes(self.manifiesto.read_bytes() + b"\n")
        with self.assertRaisesRegex(ErrorVisual, "otro mapa"):
            self.seed()
        self.assertEqual((self.almacen / self.lote / "mapa.json").read_bytes(), original)
        self.assertEqual(self.contar(PilotoVisual), 1)

    def test_version_nueva_no_reasigna_piloto_anterior(self):
        primero = self.seed()
        segundo = self.seed(version="v2")
        self.assertNotEqual(primero["piloto_id"], segundo["piloto_id"])
        self.assertEqual(self.seed()["estado"], "sin_cambios")
        self.assertEqual(self.contar(AsociacionVisual), 400)

    def test_restricciones_impiden_huerfanos_cruces_y_duplicados(self):
        self.seed()
        with Session(self.motor) as sesion:
            asociaciones = sesion.scalars(select(AsociacionVisual).order_by(AsociacionVisual.id)).all()
            primero, segundo = asociaciones[:2]
            primero_id, imagen_id, parada_id = primero.id, segundo.imagen_id, segundo.parada_id
        for cambios in ({"imagen_id": 999999}, {"parada_id": 999999}, {"piloto_id": 999999},
                        {"dataset_amazon_id": 999999}, {"dataset_visual_id": 999999},
                        {"imagen_id": imagen_id}, {"parada_id": parada_id}, {"tipo_asociacion": "real"}):
            with self.subTest(cambios=cambios), self.assertRaises(IntegrityError):
                with Session(self.motor) as sesion, sesion.begin():
                    sesion.execute(update(AsociacionVisual).where(AsociacionVisual.id == primero_id).values(**cambios))
        nuevo = importar_amazon(self.csv, replace(self.amazon, version="otro"), motor=self.motor)
        from src.persistencia.logistica import Parada
        with Session(self.motor) as sesion:
            otro_id = sesion.scalar(select(Parada.id).where(Parada.dataset_id == nuevo.dataset_id))
        with self.assertRaises(IntegrityError):
            with Session(self.motor) as sesion, sesion.begin():
                sesion.execute(update(AsociacionVisual).where(AsociacionVisual.id == primero_id).values(parada_id=otro_id))

    def test_downgrade_solo_fase4_conserva_amazon(self):
        self.seed()
        self.migrar(command.downgrade, "0002_datasets_logistica")
        from src.persistencia.logistica import Parada
        self.assertEqual(self.contar(Parada), 240)
        self.migrar(command.upgrade, "head")
        # Downgrade conserva catálogo de fuentes/auditoría; es destructivo y solo
        # se prueba aquí. No se invoca en desarrollo ni como estrategia de reintento.
        self.assertEqual(self.contar(Imagen), 0)


class MapaFijadoTests(unittest.TestCase):
    def test_mapa_real_versionado_reproduce_bytes_y_hash(self):
        from src.datos.validacion import cargar_manifiesto
        raiz = Path(__file__).resolve().parents[1]
        manifests = raiz / "data/manifests"
        contenido = (manifests / "piloto-visual-v1.json").read_bytes()
        mapa = construir_mapa((raiz / "data/amazon_pedidos.csv").read_bytes(),
            cargar_manifiesto(manifests / "amazon-v1.json"), json.loads(contenido), contenido)
        self.assertEqual(json_bytes(mapa), (manifests / "asociaciones-v1.json").read_bytes())
        self.assertEqual(hash_mapa(mapa), "d645bac9ea84ad279843a50b8ad9d0549a7a77c39fd71b7204d4a174d15332d5")

    def test_cli_error_bd_no_revela_credenciales(self):
        import subprocess
        import sys
        resultado = subprocess.run([sys.executable, "-m", "src.vision.seed"], capture_output=True, text=True,
            env={**os.environ, "DATABASE_URL": "postgresql+psycopg://usuario:secreto@127.0.0.1:1/no_existe"})
        self.assertEqual(resultado.returncode, 1)
        self.assertIn("PostgreSQL no disponible", resultado.stderr)
        self.assertNotIn("secreto", resultado.stderr)
        self.assertNotIn("Traceback", resultado.stderr)
