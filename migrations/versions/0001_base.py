"""Establece la revisión inicial sin adelantar el modelo logístico de fase 2.

La única tabla creada por esta revisión es alembic_version, gestionada por
Alembic. La fase 2 añadirá tablas de dominio mediante una revisión nueva.
"""

revision = "0001_base"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Registra la línea base del esquema vacío."""
    pass


def downgrade() -> None:
    """Retira la revisión base; todavía no hay tablas de dominio que borrar."""
    pass
