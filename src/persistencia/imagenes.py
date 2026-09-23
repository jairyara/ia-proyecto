"""Pilotos inmutables y relaciones simuladas, sin predicciones ni entrenamiento."""

from sqlalchemy import CheckConstraint, ForeignKey, ForeignKeyConstraint, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from src.persistencia.base import Base


class Imagen(Base):
    __tablename__ = "imagenes"
    __table_args__ = (
        UniqueConstraint("dataset_id", "id_origen"),
        UniqueConstraint("dataset_id", "sha256", name="uq_imagenes_dataset_sha256"),
        UniqueConstraint("dataset_id", "id", name="uq_imagenes_dataset_id_id"),
        CheckConstraint("bytes > 0 AND bytes <= 2097152 AND ancho = 960 AND alto = 540", name="limites_validos"),
        CheckConstraint("mime = 'image/png'", name="mime_valido"),
        CheckConstraint("(etiqueta = 'danado' AND etiqueta_origen = 'damaged') OR (etiqueta = 'intacto' AND etiqueta_origen = 'intact')", name="etiqueta_valida"),
        CheckConstraint("sha256 ~ '^[0-9a-f]{64}$'", name="hash_valido"),
    )
    id: Mapped[int] = mapped_column(primary_key=True)
    dataset_id: Mapped[int] = mapped_column(ForeignKey("datasets.id"))
    id_origen: Mapped[str] = mapped_column(String(80))
    clave_archivo: Mapped[str] = mapped_column(String(180), unique=True)
    sha256: Mapped[str] = mapped_column(String(64))
    mime: Mapped[str] = mapped_column(String(40))
    bytes: Mapped[int]
    ancho: Mapped[int]
    alto: Mapped[int]
    grupo_origen: Mapped[str] = mapped_column(String(80), index=True)
    etiqueta_origen: Mapped[str] = mapped_column(String(20))
    etiqueta: Mapped[str] = mapped_column(String(20))


class PilotoVisual(Base):
    __tablename__ = "pilotos_visuales"
    __table_args__ = (
        UniqueConstraint("id", "dataset_amazon_id", "dataset_visual_id", name="uq_pilotos_datasets"),
        CheckConstraint("mapa_sha256 ~ '^[0-9a-f]{64}$'", name="hash_valido"),
        CheckConstraint("semilla_paradas >= 0 AND semilla_imagenes >= 0", name="semillas_validas"),
    )
    id: Mapped[int] = mapped_column(primary_key=True)
    version: Mapped[str] = mapped_column(String(80), unique=True)
    dataset_amazon_id: Mapped[int] = mapped_column(ForeignKey("datasets.id"))
    dataset_visual_id: Mapped[int] = mapped_column(ForeignKey("datasets.id"))
    algoritmo: Mapped[str] = mapped_column(String(80))
    semilla_paradas: Mapped[int]
    semilla_imagenes: Mapped[int]
    mapa_sha256: Mapped[str] = mapped_column(String(64))
    mapa_json: Mapped[str] = mapped_column(Text)


class AsociacionVisual(Base):
    __tablename__ = "asociaciones_visuales"
    __table_args__ = (
        UniqueConstraint("piloto_id", "parada_id"),
        UniqueConstraint("piloto_id", "imagen_id", name="uq_asociaciones_piloto_imagen"),
        ForeignKeyConstraint(["piloto_id", "dataset_amazon_id", "dataset_visual_id"],
                             ["pilotos_visuales.id", "pilotos_visuales.dataset_amazon_id", "pilotos_visuales.dataset_visual_id"]),
        ForeignKeyConstraint(["dataset_amazon_id", "parada_id"], ["paradas.dataset_id", "paradas.id"]),
        ForeignKeyConstraint(["dataset_visual_id", "imagen_id"], ["imagenes.dataset_id", "imagenes.id"]),
        CheckConstraint("tipo_asociacion = 'simulada'", name="tipo_valido"),
    )
    id: Mapped[int] = mapped_column(primary_key=True)
    piloto_id: Mapped[int]
    dataset_amazon_id: Mapped[int]
    dataset_visual_id: Mapped[int]
    parada_id: Mapped[int] = mapped_column(index=True)
    imagen_id: Mapped[int] = mapped_column(index=True)
    tipo_asociacion: Mapped[str] = mapped_column(String(20))
