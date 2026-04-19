"""Agrega historial de cotizaciones de flete.

Revision ID: 0011_cotizaciones_flete
Revises: 0010_cliente_tarifas_especiales
Create Date: 2026-03-28

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0011_cotizaciones_flete"
down_revision: Union[str, Sequence[str], None] = "0010_cliente_tarifas_especiales"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "cotizaciones_flete",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("folio", sa.String(length=32), nullable=False),
        sa.Column("cliente_id", sa.Integer(), nullable=True),
        sa.Column("tarifa_flete_id", sa.Integer(), nullable=False),
        sa.Column("tarifa_especial_cliente_id", sa.Integer(), nullable=True),
        sa.Column("flete_id", sa.Integer(), nullable=True),
        sa.Column("ambito", sa.String(length=24), nullable=False),
        sa.Column("modalidad_cobro", sa.String(length=24), nullable=False),
        sa.Column("origen", sa.String(length=255), nullable=False),
        sa.Column("destino", sa.String(length=255), nullable=False),
        sa.Column("tipo_unidad", sa.String(length=64), nullable=False),
        sa.Column("tipo_carga", sa.String(length=64), nullable=True),
        sa.Column("distancia_km", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("peso_kg", sa.Numeric(precision=12, scale=3), nullable=False),
        sa.Column("horas_servicio", sa.Numeric(precision=10, scale=2), server_default="0", nullable=False),
        sa.Column("dias_servicio", sa.Numeric(precision=10, scale=2), server_default="0", nullable=False),
        sa.Column("urgencia", sa.Boolean(), server_default=sa.text("0"), nullable=False),
        sa.Column("retorno_vacio", sa.Boolean(), server_default=sa.text("0"), nullable=False),
        sa.Column("riesgo_pct_extra", sa.Numeric(precision=8, scale=4), server_default="0", nullable=False),
        sa.Column("recargos", sa.Numeric(precision=14, scale=2), server_default="0", nullable=False),
        sa.Column("costo_base_estimado", sa.Numeric(precision=14, scale=2), nullable=False),
        sa.Column("subtotal_estimado", sa.Numeric(precision=14, scale=2), nullable=False),
        sa.Column("utilidad_aplicada", sa.Numeric(precision=14, scale=2), nullable=False),
        sa.Column("riesgo_aplicado", sa.Numeric(precision=14, scale=2), nullable=False),
        sa.Column("urgencia_aplicada", sa.Numeric(precision=14, scale=2), nullable=False),
        sa.Column("retorno_vacio_aplicado", sa.Numeric(precision=14, scale=2), nullable=False),
        sa.Column("carga_especial_aplicada", sa.Numeric(precision=14, scale=2), nullable=False),
        sa.Column("descuento_cliente_aplicado", sa.Numeric(precision=14, scale=2), server_default="0", nullable=False),
        sa.Column("incremento_cliente_aplicado", sa.Numeric(precision=14, scale=2), server_default="0", nullable=False),
        sa.Column("recargo_fijo_cliente_aplicado", sa.Numeric(precision=14, scale=2), server_default="0", nullable=False),
        sa.Column("precio_venta_sugerido", sa.Numeric(precision=14, scale=2), nullable=False),
        sa.Column("moneda", sa.String(length=3), nullable=False),
        sa.Column("detalle_calculo", sa.Text(), nullable=False),
        sa.Column("estatus", sa.String(length=24), server_default="borrador", nullable=False),
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
        sa.ForeignKeyConstraint(["cliente_id"], ["clientes.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["tarifa_flete_id"], ["tarifas_flete.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(
            ["tarifa_especial_cliente_id"], ["cliente_tarifas_especiales.id"], ondelete="SET NULL"
        ),
        sa.ForeignKeyConstraint(["flete_id"], ["fletes.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_cotizaciones_flete_folio", "cotizaciones_flete", ["folio"], unique=True)
    op.create_index("ix_cotizaciones_flete_cliente_id", "cotizaciones_flete", ["cliente_id"], unique=False)
    op.create_index(
        "ix_cotizaciones_flete_tarifa_flete_id", "cotizaciones_flete", ["tarifa_flete_id"], unique=False
    )
    op.create_index(
        "ix_cotizaciones_flete_tarifa_especial_cliente_id",
        "cotizaciones_flete",
        ["tarifa_especial_cliente_id"],
        unique=False,
    )
    op.create_index("ix_cotizaciones_flete_flete_id", "cotizaciones_flete", ["flete_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_cotizaciones_flete_flete_id", table_name="cotizaciones_flete")
    op.drop_index(
        "ix_cotizaciones_flete_tarifa_especial_cliente_id",
        table_name="cotizaciones_flete",
    )
    op.drop_index("ix_cotizaciones_flete_tarifa_flete_id", table_name="cotizaciones_flete")
    op.drop_index("ix_cotizaciones_flete_cliente_id", table_name="cotizaciones_flete")
    op.drop_index("ix_cotizaciones_flete_folio", table_name="cotizaciones_flete")
    op.drop_table("cotizaciones_flete")
