"""Contratos internos de lectura, sin HTTP, acceso CSV ni escrituras implícitas."""

from dataclasses import dataclass
from datetime import date, time
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from src.persistencia.logistica import Estacion, Parada, Ruta
from src.persistencia.modelos import Dataset


@dataclass(frozen=True)
class Pagina[T]:
    items: tuple[T, ...]
    total: int
    limite: int
    offset: int


@dataclass(frozen=True)
class DatasetLectura:
    id: int
    fuente: str
    version: str
    sha256: str
    procedencia: str
    num_paradas: int
    num_rutas: int
    num_estaciones: int


@dataclass(frozen=True)
class RutaLectura:
    id: int
    dataset_id: int
    route_id: str
    station_code: str
    fecha: date
    hora_salida_utc: time
    capacidad_vehiculo_m3: Decimal


@dataclass(frozen=True)
class ParadaLectura:
    id: int
    dataset_id: int
    pedido_id: str
    route_id: str
    stop_id: str
    station_code: str
    fecha: date
    hora_salida_utc: time
    tipo_parada: str
    lat: Decimal
    lng: Decimal
    zone_id: str
    distancia_deposito_km: Decimal
    num_paquetes: int
    volumen_total_m3: Decimal
    volumen_promedio_m3: Decimal
    tiempo_servicio_seg: Decimal
    tiene_ventana_horaria: bool
    duracion_ventana_min: Decimal
    secuencia_real: int
    capacidad_vehiculo_m3: Decimal
    retrasado_estimado: bool


def _pagina(sesion, consulta, dto, limite, offset):
    if type(limite) is not int or type(offset) is not int or not 1 <= limite <= 200 or offset < 0:
        raise ValueError("Paginación inválida: limite 1–200 y offset no negativo.")
    total = sesion.scalar(select(func.count()).select_from(consulta.order_by(None).subquery()))
    items = tuple(dto(**fila) for fila in sesion.execute(consulta.limit(limite).offset(offset)).mappings())
    return Pagina(items, total, limite, offset)


def listar_datasets(sesion: Session, *, limite=50, offset=0) -> Pagina[DatasetLectura]:
    consulta = select(*(getattr(Dataset, campo) for campo in DatasetLectura.__dataclass_fields__)).where(Dataset.estado == "completo").order_by(Dataset.id)
    return _pagina(sesion, consulta, DatasetLectura, limite, offset)


def listar_rutas(sesion: Session, dataset_id: int, *, station_code: str | None = None, limite=50, offset=0) -> Pagina[RutaLectura]:
    consulta = select(
        Ruta.id, Ruta.dataset_id, Ruta.route_id, Estacion.station_code,
        Ruta.fecha, Ruta.hora_salida_utc, Ruta.capacidad_vehiculo_m3,
    ).join(Estacion).join(Dataset).where(Dataset.estado == "completo", Ruta.dataset_id == dataset_id)
    if station_code is not None:
        consulta = consulta.where(Estacion.station_code == station_code)
    return _pagina(sesion, consulta.order_by(Ruta.route_id), RutaLectura, limite, offset)


def _consulta_paradas(dataset_id):
    columnas = []
    for campo in ParadaLectura.__dataclass_fields__:
        modelo = Parada if hasattr(Parada, campo) else (Estacion if campo == "station_code" else Ruta)
        columnas.append(getattr(modelo, campo))
    return select(*columnas).select_from(Parada).join(
        Ruta, (Parada.ruta_id == Ruta.id) & (Parada.dataset_id == Ruta.dataset_id),
    ).join(Estacion, Ruta.estacion_id == Estacion.id).join(
        Dataset, Parada.dataset_id == Dataset.id,
    ).where(Parada.dataset_id == dataset_id, Dataset.estado == "completo")


def listar_paradas(
    sesion: Session, dataset_id: int, *, route_id: str | None = None,
    station_code: str | None = None, retrasado_estimado: bool | None = None,
    limite=50, offset=0,
) -> Pagina[ParadaLectura]:
    consulta = _consulta_paradas(dataset_id)
    if route_id is not None:
        consulta = consulta.where(Ruta.route_id == route_id)
    if station_code is not None:
        consulta = consulta.where(Estacion.station_code == station_code)
    if retrasado_estimado is not None:
        if type(retrasado_estimado) is not bool:
            raise ValueError("retrasado_estimado debe ser bool o None.")
        consulta = consulta.where(Parada.retrasado_estimado == retrasado_estimado)
    return _pagina(sesion, consulta.order_by(Parada.pedido_id), ParadaLectura, limite, offset)


def obtener_parada(sesion: Session, dataset_id: int, pedido_id: str) -> ParadaLectura | None:
    fila = sesion.execute(_consulta_paradas(dataset_id).where(Parada.pedido_id == pedido_id)).mappings().one_or_none()
    return ParadaLectura(**fila) if fila is not None else None
