"""Configuración privada y diferida sin requerir un servidor PostgreSQL."""

from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from src.configuracion import ErrorConfiguracion, cargar_configuracion_bd
from src.persistencia.sesion import crear_motor


class ConfiguracionBDTests(unittest.TestCase):
    def configurar(self, **valores):
        return cargar_configuracion_bd(entorno=valores, archivo_env=None)

    def test_contrasena_obligatoria_solo_al_solicitar_configuracion(self):
        with self.assertRaises(ErrorConfiguracion):
            self.configurar()

    def test_caracteres_especiales_no_rompen_credenciales(self):
        clave = "secreto@:/%# con espacios"
        config = self.configurar(POSTGRES_PASSWORD=clave)
        self.assertEqual(config.url.password, clave)
        self.assertEqual(config.url.drivername, "postgresql+psycopg")
        self.assertEqual(config.url.port, 5433)
        self.assertNotIn(clave, repr(config))
        self.assertNotIn(clave, str(config.url))

    def test_url_explicita_prevalece_sobre_campos_separados(self):
        config = self.configurar(
            DATABASE_URL="postgresql+psycopg://otro:clave@servidor:5444/otra",
            DB_HOST="ignorado", DB_PORT="no se usa",
        )
        self.assertEqual(config.url.host, "servidor")
        self.assertEqual(config.url.database, "otra")
        self.assertEqual(config.url.port, 5444)

    def test_url_invalida_no_filtra_credenciales(self):
        for url in (
            "secreto-no-es-url", "sqlite:///secreto",
            "postgresql+psycopg://usuario:secreto@host:abc/bd",
            "postgresql+psycopg://usuario:secreto@host:65536/bd",
            "postgresql+psycopg://usuario@host/bd",
        ):
            with self.subTest(url=url):
                with self.assertRaises(ErrorConfiguracion) as error:
                    self.configurar(DATABASE_URL=url)
                self.assertNotIn("secreto", str(error.exception))

    def test_puerto_y_timeout_limitados(self):
        for clave, valor in (("DB_PORT", "0"), ("DB_PORT", "65536"),
                             ("DB_PORT", "abc"), ("DB_CONNECT_TIMEOUT", "0"),
                             ("DB_CONNECT_TIMEOUT", "61")):
            with self.subTest(clave=clave, valor=valor):
                with self.assertRaises(ErrorConfiguracion):
                    self.configurar(POSTGRES_PASSWORD="clave", **{clave: valor})

    def test_entorno_prevalece_sobre_dotenv_sin_mutarlo(self):
        with TemporaryDirectory() as carpeta:
            archivo = Path(carpeta) / ".env"
            archivo.write_text("POSTGRES_PASSWORD='p@ss%${NO_EXPANDIR}'\nDB_PORT=5444\n")
            with patch.dict("os.environ", {"DB_PORT": "5555"}, clear=True):
                import os
                config = cargar_configuracion_bd(archivo_env=archivo)
                self.assertEqual(config.url.port, 5555)
                self.assertEqual(config.url.password, "p@ss%${NO_EXPANDIR}")
                self.assertNotIn("POSTGRES_PASSWORD", os.environ)

    def test_motor_no_conecta_ni_crea_tablas_al_construirse(self):
        config = self.configurar(POSTGRES_PASSWORD="clave")
        with patch("psycopg.connect", side_effect=AssertionError("No debe conectar")):
            motor = crear_motor(config)
            try:
                self.assertTrue(motor.hide_parameters)
                self.assertFalse(motor.echo)
            finally:
                motor.dispose()
