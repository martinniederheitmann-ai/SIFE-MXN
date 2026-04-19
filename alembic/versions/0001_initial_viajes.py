"""Crea la tabla viajes.

Revision ID: 0001_initial_viajes
Revises:
Create Date: 2025-03-24

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0001_initial_viajes"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "viajes",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("codigo_viaje", sa.String(length=64), nullable=False),
        sa.Column("descripcion", sa.String(length=255), nullable=True),
        sa.Column("origen", sa.String(length=255), nullable=False),
        sa.Column("destino", sa.String(length=255), nullable=False),
        sa.Column("fecha_salida", sa.DateTime(timezone=True), nullable=False),
        sa.Column("fecha_llegada_estimada", sa.DateTime(timezone=True), nullable=True),
        sa.Column("fecha_llegada_real", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "estado",
            sa.String(length=32),
            nullable=False,
            server_default="planificado",
        ),
        sa.Column("kilometros_estimados", sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column("notas", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP(6)"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP(6)"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_viajes_codigo_viaje", "viajes", ["codigo_viaje"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_viajes_codigo_viaje", table_name="viajes")
    op.drop_table("viajes")
