"""Crea fuentes versionadas, auditoría y logística Amazon sin importar datos.

Revision ID: 0002_datasets_logistica
Revises: 0001_base
"""

from alembic import op
import sqlalchemy as sa


revision = '0002_datasets_logistica'
down_revision = '0001_base'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Numeric sin escala conserva la precisión original; restricciones PostgreSQL
    # rechazan infinitos/NaN. FK compuesta impide cruzar rutas entre datasets.
    op.create_table('datasets',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('fuente', sa.String(length=80), nullable=False),
    sa.Column('version', sa.String(length=80), nullable=False),
    sa.Column('sha256', sa.String(length=64), nullable=False),
    sa.Column('procedencia', sa.Text(), nullable=False),
    sa.Column('estado', sa.String(length=20), nullable=False),
    sa.Column('num_paradas', sa.Integer(), nullable=False),
    sa.Column('num_rutas', sa.Integer(), nullable=False),
    sa.Column('num_estaciones', sa.Integer(), nullable=False),
    sa.Column('creado_en', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.CheckConstraint("estado = 'completo'", name=op.f('ck_datasets_estado_valido')),
    sa.CheckConstraint('num_paradas >= 0 AND num_rutas >= 0 AND num_estaciones >= 0', name=op.f('ck_datasets_conteos_validos')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_datasets')),
    sa.UniqueConstraint('fuente', 'version', name=op.f('uq_datasets_fuente'))
    )
    op.create_table('estaciones',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('station_code', sa.String(length=40), nullable=False),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_estaciones')),
    sa.UniqueConstraint('station_code', name=op.f('uq_estaciones_station_code'))
    )
    op.create_table('importaciones',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('dataset_id', sa.Integer(), nullable=True),
    sa.Column('fuente', sa.String(length=80), nullable=False),
    sa.Column('version', sa.String(length=80), nullable=False),
    sa.Column('sha256', sa.String(length=64), nullable=False),
    sa.Column('version_importador', sa.String(length=40), nullable=False),
    sa.Column('estado', sa.String(length=20), nullable=False),
    sa.Column('filas_leidas', sa.Integer(), nullable=False),
    sa.Column('filas_insertadas', sa.Integer(), nullable=False),
    sa.Column('error', sa.Text(), nullable=True),
    sa.Column('iniciado_en', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('terminado_en', sa.DateTime(timezone=True), nullable=True),
    sa.CheckConstraint("estado IN ('en_curso', 'completada', 'sin_cambios', 'fallida')", name=op.f('ck_importaciones_estado_valido')),
    sa.CheckConstraint('filas_leidas >= 0 AND filas_insertadas >= 0 AND filas_insertadas <= filas_leidas', name=op.f('ck_importaciones_conteos_validos')),
    sa.ForeignKeyConstraint(['dataset_id'], ['datasets.id'], name=op.f('fk_importaciones_dataset_id_datasets')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_importaciones'))
    )
    op.create_index(op.f('ix_importaciones_dataset_id'), 'importaciones', ['dataset_id'], unique=False)
    op.create_table('rutas',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('dataset_id', sa.Integer(), nullable=False),
    sa.Column('route_id', sa.String(length=100), nullable=False),
    sa.Column('estacion_id', sa.Integer(), nullable=False),
    sa.Column('fecha', sa.Date(), nullable=False),
    sa.Column('hora_salida_utc', sa.Time(), nullable=False),
    sa.Column('capacidad_vehiculo_m3', sa.Numeric(), nullable=False),
    sa.CheckConstraint("capacidad_vehiculo_m3 > 0 AND capacidad_vehiculo_m3 < 'Infinity'::numeric", name=op.f('ck_rutas_capacidad_valida')),
    sa.ForeignKeyConstraint(['dataset_id'], ['datasets.id'], name=op.f('fk_rutas_dataset_id_datasets')),
    sa.ForeignKeyConstraint(['estacion_id'], ['estaciones.id'], name=op.f('fk_rutas_estacion_id_estaciones')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_rutas')),
    sa.UniqueConstraint('dataset_id', 'id', name='uq_rutas_dataset_id_id'),
    sa.UniqueConstraint('dataset_id', 'route_id', name=op.f('uq_rutas_dataset_id'))
    )
    op.create_index(op.f('ix_rutas_estacion_id'), 'rutas', ['estacion_id'], unique=False)
    op.create_table('paradas',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('dataset_id', sa.Integer(), nullable=False),
    sa.Column('pedido_id', sa.String(length=80), nullable=False),
    sa.Column('ruta_id', sa.Integer(), nullable=False),
    sa.Column('stop_id', sa.String(length=40), nullable=False),
    sa.Column('tipo_parada', sa.String(length=20), nullable=False),
    sa.Column('lat', sa.Numeric(), nullable=False),
    sa.Column('lng', sa.Numeric(), nullable=False),
    sa.Column('zone_id', sa.String(length=80), nullable=False),
    sa.Column('distancia_deposito_km', sa.Numeric(), nullable=False),
    sa.Column('num_paquetes', sa.Integer(), nullable=False),
    sa.Column('volumen_total_m3', sa.Numeric(), nullable=False),
    sa.Column('volumen_promedio_m3', sa.Numeric(), nullable=False),
    sa.Column('tiempo_servicio_seg', sa.Numeric(), nullable=False),
    sa.Column('tiene_ventana_horaria', sa.Boolean(), nullable=False),
    sa.Column('duracion_ventana_min', sa.Numeric(), nullable=False),
    sa.Column('secuencia_real', sa.Integer(), nullable=False),
    sa.Column('retrasado_estimado', sa.Boolean(), nullable=False),
    sa.CheckConstraint("distancia_deposito_km >= 0 AND distancia_deposito_km < 'Infinity'::numeric", name=op.f('ck_paradas_distancia_deposito_km_valido')),
    sa.CheckConstraint("duracion_ventana_min >= 0 AND duracion_ventana_min < 'Infinity'::numeric", name=op.f('ck_paradas_duracion_ventana_min_valido')),
    sa.CheckConstraint("tiempo_servicio_seg >= 0 AND tiempo_servicio_seg < 'Infinity'::numeric", name=op.f('ck_paradas_tiempo_servicio_seg_valido')),
    sa.CheckConstraint("tipo_parada IN ('Station', 'Dropoff')", name=op.f('ck_paradas_tipo_valido')),
    sa.CheckConstraint("volumen_promedio_m3 >= 0 AND volumen_promedio_m3 < 'Infinity'::numeric", name=op.f('ck_paradas_volumen_promedio_m3_valido')),
    sa.CheckConstraint("volumen_total_m3 >= 0 AND volumen_total_m3 < 'Infinity'::numeric", name=op.f('ck_paradas_volumen_total_m3_valido')),
    sa.CheckConstraint('lat BETWEEN -90 AND 90 AND lng BETWEEN -180 AND 180', name=op.f('ck_paradas_coordenadas_validas')),
    sa.CheckConstraint('num_paquetes >= 0 AND secuencia_real >= 0', name=op.f('ck_paradas_enteros_validos')),
    sa.ForeignKeyConstraint(['dataset_id', 'ruta_id'], ['rutas.dataset_id', 'rutas.id'], name=op.f('fk_paradas_dataset_id_rutas')),
    sa.ForeignKeyConstraint(['dataset_id'], ['datasets.id'], name=op.f('fk_paradas_dataset_id_datasets')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_paradas')),
    sa.UniqueConstraint('dataset_id', 'pedido_id', name=op.f('uq_paradas_dataset_id')),
    sa.UniqueConstraint('ruta_id', 'stop_id', name=op.f('uq_paradas_ruta_id'))
    )
    op.create_index('ix_paradas_dataset_id_id', 'paradas', ['dataset_id', 'id'], unique=False)


def downgrade() -> None:
    # Destructivo: usar solo en BD desechable o con respaldo explícito.
    op.drop_index('ix_paradas_dataset_id_id', table_name='paradas')
    op.drop_table('paradas')
    op.drop_index(op.f('ix_rutas_estacion_id'), table_name='rutas')
    op.drop_table('rutas')
    op.drop_index(op.f('ix_importaciones_dataset_id'), table_name='importaciones')
    op.drop_table('importaciones')
    op.drop_table('estaciones')
    op.drop_table('datasets')
