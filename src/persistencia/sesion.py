"""Motor diferido y sesiones con transacciones explícitas, sin estado global."""

from contextlib import contextmanager
from collections.abc import Iterator

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session

from src.configuracion import ConfiguracionBD, cargar_configuracion_bd


def crear_motor(configuracion: ConfiguracionBD | None = None) -> Engine:
    """Construye el pool sin abrir conexiones; el llamador debe hacer dispose()."""
    config = configuracion if configuracion is not None else cargar_configuracion_bd()
    return create_engine(
        config.url,
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=5,
        pool_timeout=config.connect_timeout,
        connect_args={"connect_timeout": config.connect_timeout},
        hide_parameters=True,
        echo=False,
    )


@contextmanager
def abrir_sesion(motor: Engine) -> Iterator[Session]:
    """Entrega una sesión nueva; cierra y descarta cambios no confirmados.

    Para escribir, usar `with sesion.begin():` dentro del bloque: confirma al
    finalizar y revierte ante error. No hay commit implícito al cerrar la sesión.
    Nunca compartir una sesión entre peticiones o hilos.
    """
    with Session(motor, expire_on_commit=False) as sesion:
        yield sesion
