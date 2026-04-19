"""Agrega tarifas de compra por transportista.

Revision ID: 0013_tarifas_compra_transportista
Revises: 0012_ordenes_servicio
Create Date: 2026-04-03

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0013_tarifas_compra_transportista"
down_revision: Union[str, Sequence[str], None] = "0012_ordenes_servicio"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "tarifas_compra_transportista",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("transportista_id", sa.Integer(), nullable=False),
        sa.Column("nombre_tarifa", sa.String(length=120), nullable=False),
        sa.Column("ambito", sa.String(length=24), nullable=False),
        sa.Column("modalidad_cobro", sa.String(length=24), nullable=False),
        sa.Column("origen", sa.String(length=255), nullable=False),
        sa.Column("destino", sa.String(length=255), nullable=False),
        sa.Column("tipo_unidad", sa.String(length=64), nullable=False),
        sa.Column("tipo_carga", sa.String(length=64), nullable=True),
        sa.Column("tarifa_base", sa.Numeric(precision=14, scale=2), nullable=False),
        sa.Column("tarifa_km", sa.Numeric(precision=14, scale=4), server_default="0", nullable=False),
        sa.Column("tarifa_kg", sa.Numeric(precision=14, scale=6), server_default="0", nullable=False),
        sa.Column("tarifa_tonelada", sa.Numeric(precision=14, scale=4), server_default="0", nullable=False),
        sa.Column("tarifa_hora", sa.Numeric(precision=14, scale=2), server_default="0", nullable=False),
        sa.Column("tarifa_dia", sa.Numeric(precision=14, scale=2), server_default="0", nullable=False),
        sa.Column("recargo_minimo", sa.Numeric(precision=14, scale=2), server_default="0", nullable=False),
        sa.Column("dias_credito", sa.Integer(), server_default="0", nullable=False),
        sa.Column("moneda", sa.String(length=3), server_default="MXN", nullable=False),
        sa.Column("activo", sa.Boolean(), server_default=sa.text("1"), nullable=False),
        sa.Column("vigencia_inicio", sa.Date(), nullable=True),
        sa.Column("vigencia_fin", sa.Date(), nullable=True),
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
        sa.ForeignKeyConstraint(
            ["transportista_id"],
            ["transportistas.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_tarifas_compra_transportista_transportista_id"),
        "tarifas_compra_transportista",
        ["transportista_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_tarifas_compra_transportista_nombre_tarifa"),
        "tarifas_compra_transportista",
        ["nombre_tarifa"],
        unique=False,
    )
    op.create_index(
        op.f("ix_tarifas_compra_transportista_origen"),
        "tarifas_compra_transportista",
        ["origen"],
        unique=False,
    )
    op.create_index(
        op.f("ix_tarifas_compra_transportista_destino"),
        "tarifas_compra_transportista",
        ["destino"],
        unique=False,
    )
    op.create_index(
        op.f("ix_tarifas_compra_transportista_tipo_unidad"),
        "tarifas_compra_transportista",
        ["tipo_unidad"],
        unique=False,
    )
    op.create_index(
        op.f("ix_tarifas_compra_transportista_tipo_carga"),
        "tarifas_compra_transportista",
        ["tipo_carga"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_tarifas_compra_transportista_tipo_carga"), table_name="tarifas_compra_transportista")
    op.drop_index(op.f("ix_tarifas_compra_transportista_tipo_unidad"), table_name="tarifas_compra_transportista")
    op.drop_index(op.f("ix_tarifas_compra_transportista_destino"), table_name="tarifas_compra_transportista")
    op.drop_index(op.f("ix_tarifas_compra_transportista_origen"), table_name="tarifas_compra_transportista")
    op.drop_index(op.f("ix_tarifas_compra_transportista_nombre_tarifa"), table_name="tarifas_compra_transportista")
    op.drop_index(
        op.f("ix_tarifas_compra_transportista_transportista_id"),
        table_name="tarifas_compra_transportista",
    )
    op.drop_table("tarifas_compra_transportista")
