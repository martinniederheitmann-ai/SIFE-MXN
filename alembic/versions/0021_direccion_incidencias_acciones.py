"""Tablas de incidencias y acciones para módulo Dirección.

Revision ID: 0021_direccion_incidencias_acciones
Revises: 0020_role_direccion
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0021_direccion_incidencias_acciones"
down_revision: Union[str, Sequence[str], None] = "0020_role_direccion"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "direccion_incidencias",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("titulo", sa.String(length=160), nullable=False),
        sa.Column("modulo", sa.String(length=64), nullable=False),
        sa.Column(
            "severidad",
            sa.Enum("baja", "media", "alta", "critica", name="incidenciaseveridad", native_enum=False, length=16),
            nullable=False,
        ),
        sa.Column(
            "estatus",
            sa.Enum("abierta", "en_progreso", "resuelta", name="incidenciaestatus", native_enum=False, length=16),
            nullable=False,
        ),
        sa.Column("fecha_detectada", sa.Date(), nullable=False),
        sa.Column("detalle", sa.Text(), nullable=True),
        sa.Column("responsable", sa.String(length=120), nullable=True),
        sa.Column("resuelta_at", sa.DateTime(timezone=True), nullable=True),
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
    op.create_index("ix_direccion_incidencias_fecha_detectada", "direccion_incidencias", ["fecha_detectada"], unique=False)
    op.create_index("ix_direccion_incidencias_modulo", "direccion_incidencias", ["modulo"], unique=False)

    op.create_table(
        "direccion_acciones",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("week_start", sa.Date(), nullable=False),
        sa.Column("week_end", sa.Date(), nullable=False),
        sa.Column("titulo", sa.String(length=180), nullable=False),
        sa.Column("descripcion", sa.Text(), nullable=True),
        sa.Column("owner", sa.String(length=120), nullable=False),
        sa.Column("due_date", sa.Date(), nullable=True),
        sa.Column("impacto", sa.String(length=255), nullable=True),
        sa.Column(
            "estatus",
            sa.Enum("pendiente", "en_curso", "completada", "cancelada", name="accionestatus", native_enum=False, length=16),
            nullable=False,
        ),
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
    op.create_index("ix_direccion_acciones_week_start", "direccion_acciones", ["week_start"], unique=False)
    op.create_index("ix_direccion_acciones_week_end", "direccion_acciones", ["week_end"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_direccion_acciones_week_end", table_name="direccion_acciones")
    op.drop_index("ix_direccion_acciones_week_start", table_name="direccion_acciones")
    op.drop_table("direccion_acciones")

    op.drop_index("ix_direccion_incidencias_modulo", table_name="direccion_incidencias")
    op.drop_index("ix_direccion_incidencias_fecha_detectada", table_name="direccion_incidencias")
    op.drop_table("direccion_incidencias")
