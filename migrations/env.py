"""Entorno Alembic; migraciones solo por invocación administrativa explícita."""

from logging.config import fileConfig

from alembic import context

from src.configuracion import cargar_configuracion_bd
from src.persistencia.base import Base
from src.persistencia import modelos, logistica, imagenes  # noqa: F401 — registrar metadatos
from src.persistencia.sesion import crear_motor


config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name, disable_existing_loggers=False)

target_metadata = Base.metadata


def ejecutar_con_conexion(conexion):
    context.configure(connection=conexion, target_metadata=target_metadata, compare_type=True)
    with context.begin_transaction():
        context.run_migrations()


if context.is_offline_mode():
    # No necesita credenciales ni servidor para generar/revisar SQL.
    context.configure(
        dialect_name="postgresql",
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()
else:
    conexion = config.attributes.get("connection")
    if conexion is not None:
        # Permite a las pruebas inyectar su propia conexión desechable.
        ejecutar_con_conexion(conexion)
    else:
        motor = crear_motor(cargar_configuracion_bd())
        try:
            with motor.connect() as conexion:
                ejecutar_con_conexion(conexion)
        finally:
            motor.dispose()
