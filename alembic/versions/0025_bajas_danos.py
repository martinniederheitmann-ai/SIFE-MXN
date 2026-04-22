"""Registro operativo de bajas (personal/activo) y daños (activo/carga).

Revision ID: 0025_bajas_danos
Revises: 0024_direccion_semanal_reporte_snapshots
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0025_bajas_danos"
down_revision: Union[str, Sequence[str], None] = "0024_direccion_semanal_reporte_snapshots"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "bajas_danos",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("tipo", sa.String(length=16), nullable=False),
        sa.Column("titulo", sa.String(length=255), nullable=False),
        sa.Column("detalle", sa.Text(), nullable=True),
        sa.Column("fecha_evento", sa.Date(), nullable=False),
        sa.Column("flete_id", sa.Integer(), nullable=True),
        sa.Column("id_unidad", sa.Integer(), nullable=True),
        sa.Column("id_operador", sa.Integer(), nullable=True),
        sa.Column("estatus", sa.String(length=24), nullable=False, server_default="abierta"),
        sa.Column("costo_estimado", sa.Numeric(14, 2), nullable=True),
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
        sa.ForeignKeyConstraint(["flete_id"], ["fletes.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["id_unidad"], ["unidades.id_unidad"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["id_operador"], ["operadores.id_operador"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_bajas_danos_tipo", "bajas_danos", ["tipo"], unique=False)
    op.create_index("ix_bajas_danos_fecha_evento", "bajas_danos", ["fecha_evento"], unique=False)
    op.create_index("ix_bajas_danos_flete_id", "bajas_danos", ["flete_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_bajas_danos_flete_id", table_name="bajas_danos")
    op.drop_index("ix_bajas_danos_fecha_evento", table_name="bajas_danos")
    op.drop_index("ix_bajas_danos_tipo", table_name="bajas_danos")
    op.drop_table("bajas_danos")
