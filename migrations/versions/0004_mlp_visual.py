"""Evidencia de MLP visual en PostgreSQL.

Revision ID: 0004_mlp_visual
Revises: 0003_piloto_visual
"""

from alembic import op
import sqlalchemy as sa


revision = "0004_mlp_visual"
down_revision = "0003_piloto_visual"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "modelos_visuales",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("dataset_id", sa.Integer(), nullable=False),
        sa.Column("version", sa.String(length=80), nullable=False),
        sa.Column("manifiesto_sha256", sa.String(length=64), nullable=False),
        sa.Column("artefacto_sha256", sa.String(length=64), nullable=False),
        sa.Column("artefacto_clave", sa.String(length=180), nullable=False),
        sa.Column("metadatos_json", sa.Text(), nullable=False),
        sa.Column("creado_en", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint("manifiesto_sha256 ~ '^[0-9a-f]{64}$' AND artefacto_sha256 ~ '^[0-9a-f]{64}$'", name="ck_modelos_visuales_hashes_validos"),
        sa.ForeignKeyConstraint(["dataset_id"], ["datasets.id"], name="fk_modelos_visuales_dataset_id_datasets"),
        sa.PrimaryKeyConstraint("id", name="pk_modelos_visuales"),
        sa.UniqueConstraint("id", "dataset_id", name="uq_modelos_visuales_id_dataset"),
        sa.UniqueConstraint("version", name="uq_modelos_visuales_version"),
    )
    op.create_table(
        "muestras_modelo_visual",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("modelo_id", sa.Integer(), nullable=False),
        sa.Column("dataset_id", sa.Integer(), nullable=False),
        sa.Column("imagen_id", sa.Integer(), nullable=False),
        sa.Column("split", sa.String(length=8), nullable=False),
        sa.Column("clase_predicha", sa.String(length=20), nullable=True),
        sa.Column("probabilidad", sa.Float(), nullable=True),
        sa.CheckConstraint("split IN ('train', 'test')", name="ck_muestras_modelo_visual_split_valido"),
        sa.CheckConstraint("(split = 'train' AND clase_predicha IS NULL AND probabilidad IS NULL) OR "
                           "(split = 'test' AND clase_predicha IN ('danado', 'intacto') AND "
                           "probabilidad >= 0 AND probabilidad <= 1)", name="ck_muestras_modelo_visual_prediccion_segun_split"),
        sa.ForeignKeyConstraint(["dataset_id", "imagen_id"], ["imagenes.dataset_id", "imagenes.id"], name="fk_muestras_modelo_visual_dataset_id_imagenes"),
        sa.ForeignKeyConstraint(["modelo_id", "dataset_id"], ["modelos_visuales.id", "modelos_visuales.dataset_id"], name="fk_muestras_modelo_visual_modelo_id_modelos_visuales"),
        sa.PrimaryKeyConstraint("id", name="pk_muestras_modelo_visual"),
        sa.UniqueConstraint("modelo_id", "imagen_id", name="uq_muestras_modelo_visual_modelo_id"),
    )


def downgrade() -> None:
    op.drop_table("muestras_modelo_visual")
    op.drop_table("modelos_visuales")
