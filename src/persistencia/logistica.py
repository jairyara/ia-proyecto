"""Paradas agregadas Amazon; unidades originales y valores decimales exactos."""

from datetime import date, time
from decimal import Decimal

from sqlalchemy import Boolean, CheckConstraint, Date, ForeignKey, ForeignKeyConstraint, Index, Numeric, String, Time, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from src.persistencia.base import Base


class Estacion(Base):
    __tablename__ = "estaciones"

    id: Mapped[int] = mapped_column(primary_key=True)
    station_code: Mapped[str] = mapped_column(String(40), unique=True)


class Ruta(Base):
    __tablename__ = "rutas"
    __table_args__ = (
        UniqueConstraint("dataset_id", "route_id"),
        UniqueConstraint("dataset_id", "id", name="uq_rutas_dataset_id_id"),
        CheckConstraint("capacidad_vehiculo_m3 > 0 AND capacidad_vehiculo_m3 < 'Infinity'::numeric", name="capacidad_valida"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    dataset_id: Mapped[int] = mapped_column(ForeignKey("datasets.id"))
    route_id: Mapped[str] = mapped_column(String(100))
    estacion_id: Mapped[int] = mapped_column(ForeignKey("estaciones.id"), index=True)
    fecha: Mapped[date] = mapped_column(Date)
    hora_salida_utc: Mapped[time] = mapped_column(Time(timezone=False))
    capacidad_vehiculo_m3: Mapped[Decimal] = mapped_column(Numeric)


class Parada(Base):
    __tablename__ = "paradas"
    __table_args__ = (
        UniqueConstraint("dataset_id", "pedido_id"),
        UniqueConstraint("dataset_id", "id", name="uq_paradas_dataset_id_id"),
        UniqueConstraint("ruta_id", "stop_id"),
        ForeignKeyConstraint(["dataset_id", "ruta_id"], ["rutas.dataset_id", "rutas.id"]),
        Index("ix_paradas_dataset_id_id", "dataset_id", "id"),
        CheckConstraint("lat BETWEEN -90 AND 90 AND lng BETWEEN -180 AND 180", name="coordenadas_validas"),
        CheckConstraint("tipo_parada IN ('Station', 'Dropoff')", name="tipo_valido"),
        CheckConstraint("num_paquetes >= 0 AND secuencia_real >= 0", name="enteros_validos"),
        *(
            CheckConstraint(f"{columna} >= 0 AND {columna} < 'Infinity'::numeric", name=f"{columna}_valido")
            for columna in (
                "distancia_deposito_km", "volumen_total_m3", "volumen_promedio_m3",
                "tiempo_servicio_seg", "duracion_ventana_min",
            )
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    dataset_id: Mapped[int] = mapped_column(ForeignKey("datasets.id"))
    pedido_id: Mapped[str] = mapped_column(String(80))
    ruta_id: Mapped[int] = mapped_column()
    stop_id: Mapped[str] = mapped_column(String(40))
    tipo_parada: Mapped[str] = mapped_column(String(20))
    lat: Mapped[Decimal] = mapped_column(Numeric)
    lng: Mapped[Decimal] = mapped_column(Numeric)
    zone_id: Mapped[str] = mapped_column(String(80))
    distancia_deposito_km: Mapped[Decimal] = mapped_column(Numeric)
    num_paquetes: Mapped[int] = mapped_column()
    volumen_total_m3: Mapped[Decimal] = mapped_column(Numeric)
    volumen_promedio_m3: Mapped[Decimal] = mapped_column(Numeric)
    tiempo_servicio_seg: Mapped[Decimal] = mapped_column(Numeric)
    tiene_ventana_horaria: Mapped[bool] = mapped_column(Boolean)
    duracion_ventana_min: Mapped[Decimal] = mapped_column(Numeric)
    secuencia_real: Mapped[int] = mapped_column()
    retrasado_estimado: Mapped[bool] = mapped_column(Boolean)
