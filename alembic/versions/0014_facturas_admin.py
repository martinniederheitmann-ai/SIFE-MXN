"""Agrega facturas administrativas.

Revision ID: 0014_facturas_admin
Revises: 0013_tarifas_compra_transportista
Create Date: 2026-04-03

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0014_facturas_admin"
down_revision: Union[str, Sequence[str], None] = "0013_tarifas_compra_transportista"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "facturas",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("folio", sa.String(length=32), nullable=False),
        sa.Column("serie", sa.String(length=12), nullable=True),
        sa.Column("cliente_id", sa.Integer(), nullable=False),
        sa.Column("flete_id", sa.Integer(), nullable=True),
        sa.Column("orden_servicio_id", sa.Integer(), nullable=True),
        sa.Column("fecha_emision", sa.Date(), nullable=False),
        sa.Column("fecha_vencimiento", sa.Date(), nullable=True),
        sa.Column("concepto", sa.String(length=255), nullable=False),
        sa.Column("referencia", sa.String(length=120), nullable=True),
        sa.Column("moneda", sa.String(length=3), server_default="MXN", nullable=False),
        sa.Column("subtotal", sa.Numeric(precision=14, scale=2), nullable=False),
        sa.Column("iva_pct", sa.Numeric(precision=8, scale=4), server_default="0.16", nullable=False),
        sa.Column("iva_monto", sa.Numeric(precision=14, scale=2), server_default="0", nullable=False),
        sa.Column("retencion_monto", sa.Numeric(precision=14, scale=2), server_default="0", nullable=False),
        sa.Column("total", sa.Numeric(precision=14, scale=2), nullable=False),
        sa.Column("saldo_pendiente", sa.Numeric(precision=14, scale=2), nullable=False),
        sa.Column("forma_pago", sa.String(length=64), nullable=True),
        sa.Column("metodo_pago", sa.String(length=16), nullable=True),
        sa.Column("uso_cfdi", sa.String(length=16), nullable=True),
        sa.Column("estatus", sa.String(length=16), server_default="borrador", nullable=False),
        sa.Column("timbrada", sa.Boolean(), server_default=sa.text("0"), nullable=False),
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
        sa.ForeignKeyConstraint(["cliente_id"], ["clientes.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["flete_id"], ["fletes.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["orden_servicio_id"], ["ordenes_servicio.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_facturas_folio"), "facturas", ["folio"], unique=True)
    op.create_index(op.f("ix_facturas_cliente_id"), "facturas", ["cliente_id"], unique=False)
    op.create_index(op.f("ix_facturas_flete_id"), "facturas", ["flete_id"], unique=False)
    op.create_index(op.f("ix_facturas_orden_servicio_id"), "facturas", ["orden_servicio_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_facturas_orden_servicio_id"), table_name="facturas")
    op.drop_index(op.f("ix_facturas_flete_id"), table_name="facturas")
    op.drop_index(op.f("ix_facturas_cliente_id"), table_name="facturas")
    op.drop_index(op.f("ix_facturas_folio"), table_name="facturas")
    op.drop_table("facturas")
