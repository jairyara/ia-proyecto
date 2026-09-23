"""Metadatos de fuentes e intentos; sin conexión ni creación automática de tablas."""

from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from src.persistencia.base import Base


class Dataset(Base):
    __tablename__ = "datasets"
    __table_args__ = (
        UniqueConstraint("fuente", "version"),
        CheckConstraint("estado = 'completo'", name="estado_valido"),
        CheckConstraint("num_paradas >= 0 AND num_rutas >= 0 AND num_estaciones >= 0", name="conteos_validos"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    fuente: Mapped[str] = mapped_column(String(80))
    version: Mapped[str] = mapped_column(String(80))
    sha256: Mapped[str] = mapped_column(String(64))
    procedencia: Mapped[str] = mapped_column(Text)
    estado: Mapped[str] = mapped_column(String(20))
    num_paradas: Mapped[int] = mapped_column(Integer)
    num_rutas: Mapped[int] = mapped_column(Integer)
    num_estaciones: Mapped[int] = mapped_column(Integer)
    creado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Importacion(Base):
    __tablename__ = "importaciones"
    __table_args__ = (
        CheckConstraint("estado IN ('en_curso', 'completada', 'sin_cambios', 'fallida')", name="estado_valido"),
        CheckConstraint("filas_leidas >= 0 AND filas_insertadas >= 0 AND filas_insertadas <= filas_leidas", name="conteos_validos"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    dataset_id: Mapped[int | None] = mapped_column(ForeignKey("datasets.id"), index=True)
    fuente: Mapped[str] = mapped_column(String(80))
    version: Mapped[str] = mapped_column(String(80))
    sha256: Mapped[str] = mapped_column(String(64))
    version_importador: Mapped[str] = mapped_column(String(40))
    estado: Mapped[str] = mapped_column(String(20))
    filas_leidas: Mapped[int] = mapped_column(Integer)
    filas_insertadas: Mapped[int] = mapped_column(Integer)
    error: Mapped[str | None] = mapped_column(Text)
    iniciado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    terminado_en: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
