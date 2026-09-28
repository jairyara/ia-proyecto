"""Evidencia versionada del MLP visual; nunca altera etiquetas de origen."""

from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, Float, ForeignKey, ForeignKeyConstraint, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from src.persistencia.base import Base


class ModeloVisual(Base):
    __tablename__ = "modelos_visuales"
    __table_args__ = (
        UniqueConstraint("id", "dataset_id", name="uq_modelos_visuales_id_dataset"),
        CheckConstraint("manifiesto_sha256 ~ '^[0-9a-f]{64}$' AND artefacto_sha256 ~ '^[0-9a-f]{64}$'", name="hashes_validos"),
    )
    id: Mapped[int] = mapped_column(primary_key=True)
    dataset_id: Mapped[int] = mapped_column(ForeignKey("datasets.id"))
    version: Mapped[str] = mapped_column(String(80), unique=True)
    manifiesto_sha256: Mapped[str] = mapped_column(String(64))
    artefacto_sha256: Mapped[str] = mapped_column(String(64))
    artefacto_clave: Mapped[str] = mapped_column(String(180))
    metadatos_json: Mapped[str] = mapped_column(Text)
    creado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class MuestraModeloVisual(Base):
    __tablename__ = "muestras_modelo_visual"
    __table_args__ = (
        UniqueConstraint("modelo_id", "imagen_id"),
        ForeignKeyConstraint(["modelo_id", "dataset_id"], ["modelos_visuales.id", "modelos_visuales.dataset_id"]),
        ForeignKeyConstraint(["dataset_id", "imagen_id"], ["imagenes.dataset_id", "imagenes.id"]),
        CheckConstraint("split IN ('train', 'test')", name="split_valido"),
        CheckConstraint("(split = 'train' AND clase_predicha IS NULL AND probabilidad IS NULL) OR "
                        "(split = 'test' AND clase_predicha IN ('danado', 'intacto') AND "
                        "probabilidad >= 0 AND probabilidad <= 1)", name="prediccion_segun_split"),
    )
    id: Mapped[int] = mapped_column(primary_key=True)
    modelo_id: Mapped[int]
    dataset_id: Mapped[int]
    imagen_id: Mapped[int]
    split: Mapped[str] = mapped_column(String(8))
    clase_predicha: Mapped[str | None] = mapped_column(String(20))
    probabilidad: Mapped[float | None] = mapped_column(Float)
