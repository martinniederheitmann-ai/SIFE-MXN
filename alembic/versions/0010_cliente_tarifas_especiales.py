"""Agrega tarifas especiales por cliente.

Revision ID: 0010_cliente_tarifas_especiales
Revises: 0009_tarifas_formula_comercial
Create Date: 2026-03-28

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0010_cliente_tarifas_especiales"
down_revision: Union[str, Sequence[str], None] = "0009_tarifas_formula_comercial"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "cliente_tarifas_especiales",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("cliente_id", sa.Integer(), nullable=False),
        sa.Column("tarifa_flete_id", sa.Integer(), nullable=False),
        sa.Column("nombre_acuerdo", sa.String(length=120), nullable=False),
        sa.Column("precio_fijo", sa.Numeric(precision=14, scale=2), nullable=True),
        sa.Column("descuento_pct", sa.Numeric(precision=8, scale=4), server_default="0", nullable=False),
        sa.Column("incremento_pct", sa.Numeric(precision=8, scale=4), server_default="0", nullable=False),
        sa.Column("recargo_fijo", sa.Numeric(precision=14, scale=2), server_default="0", nullable=False),
        sa.Column("prioridad", sa.Integer(), server_default="100", nullable=False),
        sa.Column("activo", sa.Boolean(), server_default=sa.text("1"), nullable=False),
        sa.Column("vigencia_inicio", sa.DateTime(timezone=True), nullable=True),
        sa.Column("vigencia_fin", sa.DateTime(timezone=True), nullable=True),
        sa.Column("observaciones", sa.Text(), nullable=True),
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
        sa.ForeignKeyConstraint(["cliente_id"], ["clientes.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["tarifa_flete_id"], ["tarifas_flete.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_cliente_tarifas_especiales_cliente_id",
        "cliente_tarifas_especiales",
        ["cliente_id"],
        unique=False,
    )
    op.create_index(
        "ix_cliente_tarifas_especiales_tarifa_flete_id",
        "cliente_tarifas_especiales",
        ["tarifa_flete_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_cliente_tarifas_especiales_tarifa_flete_id",
        table_name="cliente_tarifas_especiales",
    )
    op.drop_index(
        "ix_cliente_tarifas_especiales_cliente_id",
        table_name="cliente_tarifas_especiales",
    )
    op.drop_table("cliente_tarifas_especiales")
