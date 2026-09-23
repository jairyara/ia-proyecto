"""Alembic offline y pruebas optativas sobre PostgreSQL real en schema aislado."""

from io import StringIO
import os
from pathlib import Path
import shutil
from tempfile import TemporaryDirectory
import unittest
from uuid import uuid4

from alembic import command
from alembic.config import Config
from sqlalchemy import Column, Integer, MetaData, Table, inspect, select, text
from sqlalchemy.orm import registry

from src.configuracion import ConfiguracionBD, cargar_configuracion_bd
from src.persistencia.sesion import abrir_sesion, crear_motor


ROOT = Path(__file__).resolve().parent.parent


def configuracion_alembic(**opciones):
    return Config(str(ROOT / "alembic.ini"), **opciones)


class MigracionesOfflineTests(unittest.TestCase):
    def test_sql_se_genera_sin_servidor_ni_credenciales(self):
        salida = StringIO()
        config = configuracion_alembic(output_buffer=salida)
        command.upgrade(config, "head", sql=True)
        self.assertIn("CREATE TABLE alembic_version", salida.getvalue())
        self.assertIn("0001_base", salida.getvalue())

    def test_plantilla_genera_revision_en_copia_desechable(self):
        with TemporaryDirectory() as carpeta:
            destino = Path(carpeta) / "migrations"
            shutil.copytree(ROOT / "migrations", destino, ignore=shutil.ignore_patterns("__pycache__"))
            config = configuracion_alembic()
            config.set_main_option("script_location", str(destino))
            revision = command.revision(config, message="revision de prueba", rev_id="prueba_fase1")
            self.assertEqual(revision.down_revision, "0003_piloto_visual")
            contenido = Path(revision.path).read_text()
            compile(contenido, revision.path, "exec")
            self.assertIn("def upgrade()", contenido)
            self.assertIn("def downgrade()", contenido)


class PostgreSQLAislado(unittest.TestCase):
    def setUp(self):
        config = cargar_configuracion_bd(
            entorno={"DATABASE_URL": os.environ["TEST_DATABASE_URL"]}, archivo_env=None,
        )
        if not config.url.database.endswith("_test"):
            raise RuntimeError("TEST_DATABASE_URL debe apuntar a una BD desechable terminada en _test.")
        self.admin = crear_motor(config)
        self.addCleanup(self.admin.dispose)
        self.schema = "prueba_" + uuid4().hex
        with self.admin.begin() as conexion:
            conexion.execute(text(f'CREATE SCHEMA "{self.schema}"'))
        self.addCleanup(self.limpiar_schema)
        url = config.url.update_query_dict({"options": f"-csearch_path={self.schema}"})
        self.motor = crear_motor(ConfiguracionBD(url=url))
        self.addCleanup(self.motor.dispose)

    def limpiar_schema(self):
        # Solo el schema aleatorio creado por esta prueba, nunca datos del usuario.
        with self.admin.begin() as conexion:
            conexion.execute(text(f'DROP SCHEMA "{self.schema}" CASCADE'))

    def migrar(self, accion, revision):
        with self.motor.begin() as conexion:
            config = configuracion_alembic()
            config.attributes["connection"] = conexion
            accion(config, revision)


@unittest.skipUnless(os.getenv("TEST_DATABASE_URL"), "Requiere TEST_DATABASE_URL; ver docs/guia-tecnica.md")
class PostgreSQLIntegracionTests(PostgreSQLAislado):

    def test_upgrade_downgrade_y_reaplicacion_en_schema_vacio(self):
        self.assertEqual(inspect(self.motor).get_table_names(), [])
        self.migrar(command.upgrade, "0001_base")
        self.migrar(command.upgrade, "0001_base")
        with self.motor.connect() as conexion:
            self.assertEqual(conexion.execute(text("SELECT version_num FROM alembic_version")).scalars().all(), ["0001_base"])
        self.assertEqual(inspect(self.motor).get_table_names(), ["alembic_version"])
        self.migrar(command.downgrade, "base")
        with self.motor.connect() as conexion:
            self.assertEqual(conexion.execute(text("SELECT count(*) FROM alembic_version")).scalar_one(), 0)
        self.migrar(command.upgrade, "head")
        with self.motor.begin() as conexion:
            config = configuracion_alembic()
            config.attributes["connection"] = conexion
            command.check(config)

    def test_sesiones_orm_confirman_revierten_y_no_comparten_estado(self):
        # Tabla exclusiva de prueba: la app nunca usa create_all para migrar.
        metadata = MetaData()
        tabla = Table("prueba_transaccion", metadata, Column("id", Integer, primary_key=True))
        metadata.create_all(self.motor)
        registro = registry(metadata=metadata)

        class Registro:
            pass

        registro.map_imperatively(Registro, tabla)
        self.addCleanup(registro.dispose)
        with abrir_sesion(self.motor) as sesion:
            with sesion.begin():
                fila = Registro()
                fila.id = 1
                sesion.add(fila)
        with self.assertRaisesRegex(RuntimeError, "revertir"):
            with abrir_sesion(self.motor) as sesion:
                with sesion.begin():
                    sesion.execute(tabla.insert().values(id=2))
                    raise RuntimeError("revertir")
        with abrir_sesion(self.motor) as sesion:
            sesion.execute(tabla.insert().values(id=3))  # Sin commit: se descarta.
        with abrir_sesion(self.motor) as primera, abrir_sesion(self.motor) as segunda:
            self.assertIsNot(primera, segunda)
            self.assertEqual(segunda.execute(select(tabla.c.id)).scalars().all(), [1])
