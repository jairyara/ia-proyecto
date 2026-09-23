"""Seed Amazon atómico, auditado e idempotente; nunca se ejecuta al iniciar HTTP."""

from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path

from sqlalchemy import Engine, insert, select, text
from sqlalchemy.orm import Session

from src.datos.validacion import CAMPOS_RUTA, AmazonValidado, ErrorValidacion, ManifiestoAmazon, validar_amazon
from src.persistencia.logistica import Estacion, Parada, Ruta
from src.persistencia.modelos import Dataset, Importacion


VERSION_IMPORTADOR = "amazon-1"
# Serializa exclusivamente este comando administrativo, incluso entre procesos.
# Transaccional: PostgreSQL libera el bloqueo al confirmar, revertir o desconectar.
LOCK_SEED_AMAZON = 2026092202


class ErrorImportacion(RuntimeError):
    """Error seguro para CLI; detalles SQL/credenciales nunca se imprimen."""


@dataclass(frozen=True)
class ResultadoSeed:
    estado: str
    dataset_id: int | None
    importacion_id: int | None
    paradas: int
    rutas: int
    estaciones: int
    filas_insertadas: int
    sha256: str


def _insertar_logistica(sesion: Session, dataset: Dataset, datos: AmazonValidado) -> None:
    estaciones = dict(sesion.execute(select(Estacion.station_code, Estacion.id)).all())
    nuevas = [dict(station_code=codigo) for codigo in datos.estaciones if codigo not in estaciones]
    if nuevas:
        estaciones.update(sesion.execute(insert(Estacion).returning(Estacion.station_code, Estacion.id), nuevas).all())
    rutas = []
    for route_id, valores in datos.rutas.items():
        rutas.append(dict(
            dataset_id=dataset.id, route_id=route_id,
            estacion_id=estaciones[valores["station_code"]],
            **{k: v for k, v in valores.items() if k != "station_code"},
        ))
    ids_rutas = dict(sesion.execute(insert(Ruta).returning(Ruta.route_id, Ruta.id), rutas).all())
    paradas = []
    for fila in datos.filas:
        paradas.append(dict(
            dataset_id=dataset.id, ruta_id=ids_rutas[fila["route_id"]],
            **{k: v for k, v in fila.items() if k not in (*CAMPOS_RUTA, "route_id")},
        ))
    sesion.execute(insert(Parada), paradas)


def importar_amazon(
    archivo: Path, manifiesto: ManifiestoAmazon, *, motor: Engine | None = None,
    dry_run: bool = False,
) -> ResultadoSeed:
    """Lee una vez. Dry-run no usa motor, configuración BD ni escribe auditoría.

    Un intento queda en_curso si el proceso se mata abruptamente; es evidencia,
    no un bloqueo para reintentar. Sin BD disponible no puede persistir auditoría.
    """
    contenido = archivo.read_bytes()
    hash_real = sha256(contenido).hexdigest()
    if dry_run:
        datos = validar_amazon(contenido, manifiesto)
        return ResultadoSeed("validado", None, None, len(datos.filas), len(datos.rutas), len(datos.estaciones), 0, hash_real)
    if motor is None:
        raise ValueError("El seed real requiere motor explícito.")
    with Session(motor) as sesion, sesion.begin():
        intento = Importacion(
            fuente=manifiesto.fuente, version=manifiesto.version, sha256=hash_real,
            version_importador=VERSION_IMPORTADOR, estado="en_curso",
            filas_leidas=0, filas_insertadas=0,
        )
        sesion.add(intento)
        sesion.flush()
        intento_id = intento.id
    datos = None
    try:
        datos = validar_amazon(contenido, manifiesto)
        with Session(motor) as sesion, sesion.begin():
            sesion.execute(text("SELECT pg_advisory_xact_lock(:clave)"), {"clave": LOCK_SEED_AMAZON})
            dataset = sesion.scalar(select(Dataset).where(
                Dataset.fuente == manifiesto.fuente, Dataset.version == manifiesto.version,
            ))
            estado, insertadas = "sin_cambios", 0
            if dataset is not None:
                if dataset.sha256 != hash_real:
                    raise ErrorValidacion("La versión ya existe con otro SHA-256; crea una versión nueva.")
                if (dataset.num_paradas, dataset.num_rutas, dataset.num_estaciones, dataset.procedencia) != (
                    manifiesto.paradas, manifiesto.rutas, manifiesto.estaciones, manifiesto.procedencia,
                ):
                    raise ErrorValidacion("El manifiesto difiere de la versión ya registrada.")
            else:
                dataset = Dataset(
                    fuente=manifiesto.fuente, version=manifiesto.version, sha256=hash_real,
                    procedencia=manifiesto.procedencia, estado="completo",
                    num_paradas=len(datos.filas), num_rutas=len(datos.rutas), num_estaciones=len(datos.estaciones),
                )
                sesion.add(dataset)
                sesion.flush()
                _insertar_logistica(sesion, dataset, datos)
                estado, insertadas = "completada", len(datos.filas)
            intento = sesion.get(Importacion, intento_id)
            intento.dataset_id, intento.estado = dataset.id, estado
            intento.filas_leidas, intento.filas_insertadas = len(datos.filas), insertadas
            intento.terminado_en = datetime.now(timezone.utc)
            resultado = ResultadoSeed(estado, dataset.id, intento_id, len(datos.filas), len(datos.rutas), len(datos.estaciones), insertadas, hash_real)
        return resultado
    except Exception as exc:
        mensaje = str(exc) if isinstance(exc, ErrorValidacion) else "Falló la transacción; no se publicó una carga parcial."
        try:
            with Session(motor) as sesion, sesion.begin():
                intento = sesion.get(Importacion, intento_id)
                intento.estado, intento.error = "fallida", mensaje
                intento.filas_leidas = len(datos.filas) if datos is not None else 0
                intento.terminado_en = datetime.now(timezone.utc)
        except Exception:
            raise ErrorImportacion("Falló el seed y no fue posible actualizar la auditoría; revisa el intento en_curso antes de reintentar.") from None
        if isinstance(exc, ErrorValidacion):
            raise
        raise ErrorImportacion(mensaje) from None
