"""Crea tabla de gastos de viaje.

Revision ID: 0007_gastos_viaje
Revises: 0006_tarifas_flete
Create Date: 2026-03-28

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0007_gastos_viaje"
down_revision: Union[str, Sequence[str], None] = "0006_tarifas_flete"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "gastos_viaje",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("flete_id", sa.Integer(), nullable=False),
        sa.Column("tipo_gasto", sa.String(length=64), nullable=False),
        sa.Column("monto", sa.Numeric(precision=14, scale=2), nullable=False),
        sa.Column("fecha_gasto", sa.Date(), nullable=False),
        sa.Column("descripcion", sa.Text(), nullable=True),
        sa.Column("referencia", sa.String(length=120), nullable=True),
        sa.Column("comprobante", sa.String(length=1024), nullable=True),
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
        sa.ForeignKeyConstraint(["flete_id"], ["fletes.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_gastos_viaje_flete_id", "gastos_viaje", ["flete_id"], unique=False)
    op.create_index("ix_gastos_viaje_tipo_gasto", "gastos_viaje", ["tipo_gasto"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_gastos_viaje_tipo_gasto", table_name="gastos_viaje")
    op.drop_index("ix_gastos_viaje_flete_id", table_name="gastos_viaje")
    op.drop_table("gastos_viaje")
