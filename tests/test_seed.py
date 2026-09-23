"""Validación independiente y seed sobre PostgreSQL real con schemas desechables."""

from concurrent.futures import ThreadPoolExecutor
import csv
from dataclasses import asdict, replace
from decimal import Decimal
from hashlib import sha256
from io import StringIO
import json
import os
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from alembic import command
from sqlalchemy import event, func, inspect, select, text, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.datos.consulta import listar_datasets, listar_paradas, listar_rutas, obtener_parada
from src.datos.importacion import ErrorImportacion, _insertar_logistica, importar_amazon
from src.datos.validacion import COLUMNAS, ErrorValidacion, ManifiestoAmazon, cargar_manifiesto, validar_amazon
from src.persistencia.logistica import Estacion, Parada, Ruta
from src.persistencia.modelos import Dataset, Importacion
from test_migraciones import PostgreSQLAislado, configuracion_alembic


ROOT = Path(__file__).resolve().parent.parent
FIXTURE = ROOT / "tests/fixtures/amazon_minimo.csv"


def manifiesto_fixture(contenido=None, version="fixture-v1"):
    contenido = FIXTURE.read_bytes() if contenido is None else contenido
    return ManifiestoAmazon("amazon-logistica", version, sha256(contenido).hexdigest(), "Fixture de 4 paradas del CSV histórico.", 4, 2, 2)


def csv_modificado(cambios=None, transformar=None):
    filas = list(csv.DictReader(StringIO(FIXTURE.read_text())))
    if cambios:
        filas[0].update(cambios)
    if transformar:
        transformar(filas)
    salida = StringIO(newline="")
    escritor = csv.DictWriter(salida, fieldnames=COLUMNAS)
    escritor.writeheader()
    escritor.writerows(filas)
    return salida.getvalue().encode()


class ValidacionAmazonTests(unittest.TestCase):
    def test_exports_historicos_del_paquete_datos_se_conservan(self):
        import src.datos as datos
        for nombre in datos.__all__:
            self.assertTrue(callable(getattr(datos, nombre)), nombre)
        self.assertEqual(len(datos.__all__), 6)

    def test_csv_completo_y_manifiesto_conservan_unidades(self):
        manifiesto = cargar_manifiesto(ROOT / "data/manifests/amazon-v1.json")
        datos = validar_amazon((ROOT / "data/amazon_pedidos.csv").read_bytes(), manifiesto)
        self.assertEqual((len(datos.filas), len(datos.rutas), len(datos.estaciones)), (14411, 100, 17))
        self.assertEqual(datos.filas[0]["volumen_total_m3"], Decimal("0.0312"))
        self.assertEqual(datos.filas[0]["tiempo_servicio_seg"], Decimal("79.0"))
        self.assertEqual(datos.filas[0]["hora_salida_utc"].isoformat(), "15:30:00")

    def test_dry_run_no_toca_motor_ni_archivos(self):
        with patch("src.datos.importacion.Session", side_effect=AssertionError("No conectar")):
            resultado = importar_amazon(FIXTURE, manifiesto_fixture(), dry_run=True)
        self.assertEqual(resultado.estado, "validado")
        self.assertEqual(resultado.filas_insertadas, 0)
        self.assertIsNone(resultado.dataset_id)

    def test_cli_dry_run_sin_configuracion_bd(self):
        entorno = {**os.environ, "DATABASE_URL": "invalida"}
        proceso = subprocess.run([sys.executable, "-m", "src.datos.seed", "--dry-run"], cwd=ROOT, env=entorno, capture_output=True, text=True)
        self.assertEqual(proceso.returncode, 0, proceso.stderr)
        self.assertEqual(json.loads(proceso.stdout)["paradas"], 14411)

    def test_cli_error_no_revela_url(self):
        entorno = {**os.environ, "DATABASE_URL": "postgresql+psycopg://usuario:secreto@localhost:999999/base"}
        proceso = subprocess.run([sys.executable, "-m", "src.datos.seed"], cwd=ROOT, env=entorno, capture_output=True, text=True)
        self.assertEqual(proceso.returncode, 1)
        self.assertNotIn("secreto", proceso.stderr)
        self.assertNotIn("Traceback", proceso.stderr)

    def test_hash_alterado(self):
        with self.assertRaisesRegex(ErrorValidacion, "SHA-256"):
            validar_amazon(FIXTURE.read_bytes() + b"\n", manifiesto_fixture())

    def test_conteos_diferentes(self):
        with self.assertRaisesRegex(ErrorValidacion, "Conteos"):
            validar_amazon(FIXTURE.read_bytes(), replace(manifiesto_fixture(), paradas=5))

    def test_manifiesto_invalido(self):
        for cambios in ({"sha256": "abc"}, {"version": ""}, {"fuente": "otro"}, {"paradas": True}, {"rutas": 0}, {"procedencia": ""}):
            with self.subTest(cambios=cambios), self.assertRaises(ErrorValidacion):
                replace(manifiesto_fixture(), **cambios)

    def test_valores_invalidos_se_rechazan_con_linea(self):
        for cambios in (
            {"num_paquetes": "1.5"}, {"num_paquetes": "-1"}, {"num_paquetes": "2147483648"},
            {"volumen_total_m3": "-1"}, {"volumen_total_m3": "NaN"}, {"lat": "Infinity"},
            {"lat": "91"}, {"lng": "-181"}, {"capacidad_vehiculo_m3": "0"},
            {"tiene_ventana_horaria": "2"}, {"retrasado_estimado": "true"},
            {"fecha": "2018-02-30"}, {"hora_salida_utc": "25:00:00"},
            {"hora_salida_utc": "15:30:00+00:00"}, {"tipo_parada": "otro"},
            {"pedido_id": ""}, {"zone_id": " zona"}, {"stop_id": "x" * 41},
        ):
            contenido = csv_modificado(cambios)
            with self.subTest(cambios=cambios), self.assertRaisesRegex(ErrorValidacion, "Fila 2"):
                validar_amazon(contenido, manifiesto_fixture(contenido))

    def test_duplicados_y_ruta_inconsistente(self):
        for campo in ("pedido_id", "stop_id", "fecha", "station_code", "capacidad_vehiculo_m3"):
            def cambiar(filas):
                filas[0][campo] = filas[1][campo] if campo in ("pedido_id", "stop_id") else {
                    "fecha": "2018-01-01", "station_code": "OTRA", "capacidad_vehiculo_m3": "1.5",
                }[campo]
            contenido = csv_modificado(transformar=cambiar)
            with self.subTest(campo=campo), self.assertRaises(ErrorValidacion):
                validar_amazon(contenido, manifiesto_fixture(contenido))

    def test_archivo_corrupto_cabecera_y_campos_extra(self):
        for contenido in (b"\xff\xfe", b"", b"pedido_id,pedido_id\na,b\n", FIXTURE.read_bytes().replace(b"AMZ-00001,", b"AMZ-00001,sobrante,", 1)):
            with self.subTest(contenido=contenido[:30]), self.assertRaises(ErrorValidacion):
                validar_amazon(contenido, manifiesto_fixture(contenido))


@unittest.skipUnless(os.getenv("TEST_DATABASE_URL"), "Requiere TEST_DATABASE_URL; ver docs/guia-tecnica.md")
class SeedPostgreSQLTests(PostgreSQLAislado):
    def setUp(self):
        super().setUp()
        self.migrar(command.upgrade, "head")

    def seed(self, **opciones):
        return importar_amazon(FIXTURE, manifiesto_fixture(), motor=self.motor, **opciones)

    def contar(self, modelo):
        with Session(self.motor) as sesion:
            return sesion.scalar(select(func.count()).select_from(modelo))

    def test_migracion_repetida_downgrade_y_metadata(self):
        self.migrar(command.upgrade, "head")
        self.assertEqual(set(inspect(self.motor).get_table_names()), {"alembic_version", "datasets", "importaciones", "estaciones", "rutas", "paradas", "imagenes", "pilotos_visuales", "asociaciones_visuales"})
        self.seed()
        self.migrar(command.downgrade, "0001_base")
        self.assertEqual(inspect(self.motor).get_table_names(), ["alembic_version"])
        self.migrar(command.upgrade, "head")
        with self.motor.begin() as conexion:
            config = configuracion_alembic()
            config.attributes["connection"] = conexion
            command.check(config)
        self.assertEqual(self.seed().paradas, 4)

    def test_seed_idempotente_y_auditoria(self):
        primero, segundo = self.seed(), self.seed()
        self.assertEqual(primero.dataset_id, segundo.dataset_id)
        self.assertEqual((primero.estado, segundo.estado), ("completada", "sin_cambios"))
        self.assertEqual(segundo.filas_insertadas, 0)
        self.assertEqual([self.contar(m) for m in (Dataset, Estacion, Ruta, Parada, Importacion)], [1, 2, 2, 4, 2])
        with Session(self.motor) as sesion:
            intentos = sesion.scalars(select(Importacion).order_by(Importacion.id)).all()
            self.assertEqual([i.filas_insertadas for i in intentos], [4, 0])
            self.assertTrue(all(i.terminado_en and i.filas_leidas == 4 for i in intentos))

    def test_importaciones_concurrentes_no_duplican(self):
        with ThreadPoolExecutor(max_workers=2) as ejecutor:
            resultados = list(ejecutor.map(lambda _: self.seed(), range(2)))
        self.assertEqual({r.estado for r in resultados}, {"completada", "sin_cambios"})
        self.assertEqual(self.contar(Parada), 4)
        self.assertEqual(self.contar(Dataset), 1)

    def test_error_validacion_auditado_sin_datos(self):
        with self.assertRaises(ErrorValidacion):
            importar_amazon(FIXTURE, replace(manifiesto_fixture(), sha256="0" * 64), motor=self.motor)
        self.assertEqual(self.contar(Dataset), 0)
        with Session(self.motor) as sesion:
            intento = sesion.scalar(select(Importacion))
            self.assertEqual(intento.estado, "fallida")
            self.assertIn("SHA-256", intento.error)
        self.assertEqual(self.seed().estado, "completada")

    def test_fallo_despues_de_insertar_revierte_todo_y_permite_reintento(self):
        def fallar(*args):
            _insertar_logistica(*args)
            raise RuntimeError("error interno secreto")
        with patch("src.datos.importacion._insertar_logistica", side_effect=fallar):
            with self.assertRaises(ErrorImportacion):
                self.seed()
        self.assertEqual([self.contar(m) for m in (Dataset, Estacion, Ruta, Parada)], [0, 0, 0, 0])
        with Session(self.motor) as sesion:
            intento = sesion.scalar(select(Importacion))
            self.assertEqual(intento.estado, "fallida")
            self.assertNotIn("secreto", intento.error)
        self.assertEqual(self.seed().estado, "completada")

    def test_fallo_antes_de_commit_revierte_publicacion(self):
        def fallar_commit(sesion):
            if any(isinstance(o, Importacion) and o.estado == "completada" for o in sesion.dirty):
                raise RuntimeError("commit simulado")
        event.listen(Session, "before_commit", fallar_commit)
        try:
            with self.assertRaises(ErrorImportacion):
                self.seed()
        finally:
            event.remove(Session, "before_commit", fallar_commit)
        self.assertEqual(self.contar(Parada), 0)
        self.assertEqual(self.seed().estado, "completada")

    def test_fuente_cambiada_exige_nueva_version_sin_sobrescribir(self):
        inicial = self.seed()
        contenido = csv_modificado({"volumen_total_m3": "0.1234567890123456789"})
        with TemporaryDirectory() as carpeta:
            archivo = Path(carpeta) / "cambiado.csv"
            archivo.write_bytes(contenido)
            with self.assertRaisesRegex(ErrorValidacion, "versión nueva"):
                importar_amazon(archivo, manifiesto_fixture(contenido), motor=self.motor)
            nuevo = importar_amazon(archivo, manifiesto_fixture(contenido, version="fixture-v2"), motor=self.motor)
        self.assertNotEqual(inicial.dataset_id, nuevo.dataset_id)
        self.assertEqual(self.contar(Parada), 8)
        self.assertEqual(self.contar(Estacion), 2)
        with Session(self.motor) as sesion:
            self.assertEqual(obtener_parada(sesion, inicial.dataset_id, "AMZ-00001").volumen_total_m3, Decimal("0.0312"))
            self.assertEqual(obtener_parada(sesion, nuevo.dataset_id, "AMZ-00001").volumen_total_m3, Decimal("0.1234567890123456789"))

    def test_consultas_paginadas_filtros_y_detalle(self):
        resultado = self.seed()
        with Session(self.motor) as sesion:
            self.assertEqual(listar_datasets(sesion).total, 1)
            rutas = listar_rutas(sesion, resultado.dataset_id)
            self.assertEqual(rutas.total, 2)
            pagina = listar_paradas(sesion, resultado.dataset_id, limite=2)
            siguiente = listar_paradas(sesion, resultado.dataset_id, limite=2, offset=2)
            self.assertEqual(pagina.total, 4)
            self.assertFalse({p.id for p in pagina.items} & {p.id for p in siguiente.items})
            self.assertEqual(listar_paradas(sesion, resultado.dataset_id, route_id=rutas.items[0].route_id).total, 2)
            self.assertEqual(listar_paradas(sesion, resultado.dataset_id, station_code="inexistente").total, 0)
            self.assertTrue(all(not p.retrasado_estimado for p in listar_paradas(sesion, resultado.dataset_id, retrasado_estimado=False).items))
            self.assertIsNone(obtener_parada(sesion, resultado.dataset_id, "inexistente"))
            self.assertIsNone(obtener_parada(sesion, -1, "AMZ-00001"))
            self.assertEqual(listar_rutas(sesion, resultado.dataset_id, station_code="inexistente").total, 0)
            for limite, offset in ((0, 0), (201, 0), (1, -1), (True, 0)):
                with self.assertRaises(ValueError):
                    listar_paradas(sesion, resultado.dataset_id, limite=limite, offset=offset)

    def test_restricciones_bd_impiden_huerfanos_duplicados_y_rangos_invalidos(self):
        self.seed()
        for cambios in ({"ruta_id": 999999}, {"dataset_id": 999999}, {"lat": 91}, {"num_paquetes": -1}, {"volumen_total_m3": Decimal("NaN")}, {"tiempo_servicio_seg": Decimal("Infinity")}, {"pedido_id": "AMZ-00002"}):
            with self.subTest(cambios=cambios), self.assertRaises(IntegrityError):
                with Session(self.motor) as sesion, sesion.begin():
                    sesion.execute(update(Parada).where(Parada.pedido_id == "AMZ-00001").values(**cambios))

    def test_fk_compuesta_impide_ruta_de_otro_dataset(self):
        primero = self.seed()
        segundo = importar_amazon(FIXTURE, replace(manifiesto_fixture(), version="fixture-v2"), motor=self.motor)
        with Session(self.motor) as sesion:
            ruta_id = sesion.scalar(select(Ruta.id).where(Ruta.dataset_id == segundo.dataset_id))
        with self.assertRaises(IntegrityError):
            with Session(self.motor) as sesion, sesion.begin():
                sesion.execute(update(Parada).where(Parada.dataset_id == primero.dataset_id).values(ruta_id=ruta_id))

    def test_csv_real_14411_paradas_100_rutas_y_todos_los_valores(self):
        archivo = ROOT / "data/amazon_pedidos.csv"
        manifiesto = cargar_manifiesto(ROOT / "data/manifests/amazon-v1.json")
        primero = importar_amazon(archivo, manifiesto, motor=self.motor)
        segundo = importar_amazon(archivo, manifiesto, motor=self.motor)
        self.assertEqual((primero.paradas, primero.rutas, primero.estaciones), (14411, 100, 17))
        self.assertEqual(segundo.filas_insertadas, 0)
        self.assertEqual([self.contar(m) for m in (Parada, Ruta, Estacion)], [14411, 100, 17])
        esperadas = sorted(validar_amazon(archivo.read_bytes(), manifiesto).filas, key=lambda f: f["pedido_id"])
        with Session(self.motor) as sesion:
            for offset in range(0, len(esperadas), 200):
                pagina = listar_paradas(sesion, primero.dataset_id, limite=200, offset=offset)
                for actual, esperada in zip(pagina.items, esperadas[offset:offset + 200], strict=True):
                    valores = asdict(actual)
                    del valores["id"], valores["dataset_id"]
                    self.assertEqual(valores, esperada)
