"""Persistir piloto visual y asociaciones simuladas

Revision ID: 0003_piloto_visual
Revises: 0002_datasets_logistica
"""

from alembic import op
import sqlalchemy as sa


revision = '0003_piloto_visual'
down_revision = '0002_datasets_logistica'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_unique_constraint('uq_paradas_dataset_id_id', 'paradas', ['dataset_id', 'id'])
    op.create_table('imagenes',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('dataset_id', sa.Integer(), nullable=False),
    sa.Column('id_origen', sa.String(length=80), nullable=False),
    sa.Column('clave_archivo', sa.String(length=180), nullable=False),
    sa.Column('sha256', sa.String(length=64), nullable=False),
    sa.Column('mime', sa.String(length=40), nullable=False),
    sa.Column('bytes', sa.Integer(), nullable=False),
    sa.Column('ancho', sa.Integer(), nullable=False),
    sa.Column('alto', sa.Integer(), nullable=False),
    sa.Column('grupo_origen', sa.String(length=80), nullable=False),
    sa.Column('etiqueta_origen', sa.String(length=20), nullable=False),
    sa.Column('etiqueta', sa.String(length=20), nullable=False),
    sa.CheckConstraint("(etiqueta = 'danado' AND etiqueta_origen = 'damaged') OR (etiqueta = 'intacto' AND etiqueta_origen = 'intact')", name=op.f('ck_imagenes_etiqueta_valida')),
    sa.CheckConstraint("mime = 'image/png'", name=op.f('ck_imagenes_mime_valido')),
    sa.CheckConstraint("sha256 ~ '^[0-9a-f]{64}$'", name=op.f('ck_imagenes_hash_valido')),
    sa.CheckConstraint('bytes > 0 AND bytes <= 2097152 AND ancho = 960 AND alto = 540', name=op.f('ck_imagenes_limites_validos')),
    sa.ForeignKeyConstraint(['dataset_id'], ['datasets.id'], name=op.f('fk_imagenes_dataset_id_datasets')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_imagenes')),
    sa.UniqueConstraint('clave_archivo', name=op.f('uq_imagenes_clave_archivo')),
    sa.UniqueConstraint('dataset_id', 'id', name='uq_imagenes_dataset_id_id'),
    sa.UniqueConstraint('dataset_id', 'id_origen', name=op.f('uq_imagenes_dataset_id')),
    sa.UniqueConstraint('dataset_id', 'sha256', name='uq_imagenes_dataset_sha256')
    )
    op.create_index(op.f('ix_imagenes_grupo_origen'), 'imagenes', ['grupo_origen'], unique=False)
    op.create_table('pilotos_visuales',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('version', sa.String(length=80), nullable=False),
    sa.Column('dataset_amazon_id', sa.Integer(), nullable=False),
    sa.Column('dataset_visual_id', sa.Integer(), nullable=False),
    sa.Column('algoritmo', sa.String(length=80), nullable=False),
    sa.Column('semilla_paradas', sa.Integer(), nullable=False),
    sa.Column('semilla_imagenes', sa.Integer(), nullable=False),
    sa.Column('mapa_sha256', sa.String(length=64), nullable=False),
    sa.Column('mapa_json', sa.Text(), nullable=False),
    sa.CheckConstraint("mapa_sha256 ~ '^[0-9a-f]{64}$'", name=op.f('ck_pilotos_visuales_hash_valido')),
    sa.CheckConstraint('semilla_paradas >= 0 AND semilla_imagenes >= 0', name=op.f('ck_pilotos_visuales_semillas_validas')),
    sa.ForeignKeyConstraint(['dataset_amazon_id'], ['datasets.id'], name=op.f('fk_pilotos_visuales_dataset_amazon_id_datasets')),
    sa.ForeignKeyConstraint(['dataset_visual_id'], ['datasets.id'], name=op.f('fk_pilotos_visuales_dataset_visual_id_datasets')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_pilotos_visuales')),
    sa.UniqueConstraint('id', 'dataset_amazon_id', 'dataset_visual_id', name='uq_pilotos_datasets'),
    sa.UniqueConstraint('version', name=op.f('uq_pilotos_visuales_version'))
    )
    op.create_table('asociaciones_visuales',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('piloto_id', sa.Integer(), nullable=False),
    sa.Column('dataset_amazon_id', sa.Integer(), nullable=False),
    sa.Column('dataset_visual_id', sa.Integer(), nullable=False),
    sa.Column('parada_id', sa.Integer(), nullable=False),
    sa.Column('imagen_id', sa.Integer(), nullable=False),
    sa.Column('tipo_asociacion', sa.String(length=20), nullable=False),
    sa.CheckConstraint("tipo_asociacion = 'simulada'", name=op.f('ck_asociaciones_visuales_tipo_valido')),
    sa.ForeignKeyConstraint(['dataset_amazon_id', 'parada_id'], ['paradas.dataset_id', 'paradas.id'], name=op.f('fk_asociaciones_visuales_dataset_amazon_id_paradas')),
    sa.ForeignKeyConstraint(['dataset_visual_id', 'imagen_id'], ['imagenes.dataset_id', 'imagenes.id'], name=op.f('fk_asociaciones_visuales_dataset_visual_id_imagenes')),
    sa.ForeignKeyConstraint(['piloto_id', 'dataset_amazon_id', 'dataset_visual_id'], ['pilotos_visuales.id', 'pilotos_visuales.dataset_amazon_id', 'pilotos_visuales.dataset_visual_id'], name=op.f('fk_asociaciones_visuales_piloto_id_pilotos_visuales')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_asociaciones_visuales')),
    sa.UniqueConstraint('piloto_id', 'imagen_id', name='uq_asociaciones_piloto_imagen'),
    sa.UniqueConstraint('piloto_id', 'parada_id', name=op.f('uq_asociaciones_visuales_piloto_id'))
    )
    op.create_index(op.f('ix_asociaciones_visuales_imagen_id'), 'asociaciones_visuales', ['imagen_id'], unique=False)
    op.create_index(op.f('ix_asociaciones_visuales_parada_id'), 'asociaciones_visuales', ['parada_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_asociaciones_visuales_parada_id'), table_name='asociaciones_visuales')
    op.drop_index(op.f('ix_asociaciones_visuales_imagen_id'), table_name='asociaciones_visuales')
    op.drop_table('asociaciones_visuales')
    op.drop_table('pilotos_visuales')
    op.drop_index(op.f('ix_imagenes_grupo_origen'), table_name='imagenes')
    op.drop_table('imagenes')
    op.drop_constraint('uq_paradas_dataset_id_id', 'paradas', type_='unique')
