"""Configuración de persistencia leída solo cuando un flujo nuevo la solicita."""

from __future__ import annotations

from dataclasses import dataclass, field
import os
from pathlib import Path
from typing import Mapping

from dotenv import dotenv_values
from sqlalchemy.engine import URL, make_url
from sqlalchemy.exc import ArgumentError


ROOT = Path(__file__).resolve().parent.parent


class ErrorConfiguracion(ValueError):
    """Configuración ausente o inválida, sin revelar credenciales."""


@dataclass(frozen=True)
class ConfiguracionBD:
    """URL privada y plazo máximo de conexión para PostgreSQL con psycopg 3."""

    url: URL = field(repr=False)
    connect_timeout: int = 3


def _entero(valores: Mapping[str, str], clave: str, defecto: str, maximo: int) -> int:
    try:
        valor = int(valores.get(clave, defecto))
    except (ValueError, TypeError):
        raise ErrorConfiguracion(f"{clave} debe ser un entero positivo.") from None
    if not 1 <= valor <= maximo:
        raise ErrorConfiguracion(f"{clave} debe estar entre 1 y {maximo}.")
    return valor


def cargar_configuracion_bd(
    *,
    entorno: Mapping[str, str] | None = None,
    archivo_env: Path | None = ROOT / ".env",
) -> ConfiguracionBD:
    """Lee .env sin mutar os.environ; las variables del proceso prevalecen.

    No lee configuración ni abre conexiones al importar el módulo. Pasar
    archivo_env=None permite pruebas y comandos aislados del .env local.
    """
    valores = {}
    if archivo_env is not None:
        valores.update(
            {k: v for k, v in dotenv_values(archivo_env, interpolate=False).items() if v is not None}
        )
    valores.update(os.environ if entorno is None else entorno)
    timeout = _entero(valores, "DB_CONNECT_TIMEOUT", "3", 60)
    url_texto = valores.get("DATABASE_URL", "")
    if url_texto:
        try:
            url = make_url(url_texto)
            puerto = url.port
        except (ValueError, TypeError, ArgumentError):
            raise ErrorConfiguracion("DATABASE_URL no es una URL válida.") from None
        if url.drivername != "postgresql+psycopg":
            raise ErrorConfiguracion("DATABASE_URL debe usar postgresql+psycopg://.")
        if puerto is not None and not 1 <= puerto <= 65535:
            raise ErrorConfiguracion("El puerto de DATABASE_URL no es válido.")
    else:
        url = URL.create(
            "postgresql+psycopg",
            username=valores.get("POSTGRES_USER", "ia_app"),
            password=valores.get("POSTGRES_PASSWORD"),
            host=valores.get("DB_HOST", "127.0.0.1"),
            port=_entero(valores, "DB_PORT", "5433", 65535),
            database=valores.get("POSTGRES_DB", "ia_logistica"),
        )
    if not all((url.host, url.database, url.username, url.password)):
        raise ErrorConfiguracion(
            "Configura host, base, usuario y contraseña de PostgreSQL; "
            "usa .env.example como referencia."
        )
    return ConfiguracionBD(url=url, connect_timeout=timeout)
