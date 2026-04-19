"""Agrega ordenes de servicio.

Revision ID: 0012_ordenes_servicio
Revises: 0011_cotizaciones_flete
Create Date: 2026-03-28

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0012_ordenes_servicio"
down_revision: Union[str, Sequence[str], None] = "0011_cotizaciones_flete"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "ordenes_servicio",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("folio", sa.String(length=32), nullable=False),
        sa.Column("cliente_id", sa.Integer(), nullable=False),
        sa.Column("cotizacion_id", sa.Integer(), nullable=True),
        sa.Column("flete_id", sa.Integer(), nullable=True),
        sa.Column("viaje_id", sa.Integer(), nullable=True),
        sa.Column("despacho_id", sa.Integer(), nullable=True),
        sa.Column("origen", sa.String(length=255), nullable=False),
        sa.Column("destino", sa.String(length=255), nullable=False),
        sa.Column("tipo_unidad", sa.String(length=64), nullable=False),
        sa.Column("tipo_carga", sa.String(length=64), nullable=True),
        sa.Column("peso_kg", sa.Numeric(precision=12, scale=3), nullable=False),
        sa.Column("distancia_km", sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column("precio_comprometido", sa.Numeric(precision=14, scale=2), nullable=False),
        sa.Column("moneda", sa.String(length=3), server_default="MXN", nullable=False),
        sa.Column(
            "fecha_solicitud",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP(6)"),
            nullable=False,
        ),
        sa.Column("fecha_programada", sa.DateTime(timezone=True), nullable=True),
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
        sa.ForeignKeyConstraint(["cliente_id"], ["clientes.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["cotizacion_id"], ["cotizaciones_flete.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["flete_id"], ["fletes.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["viaje_id"], ["viajes.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["despacho_id"], ["despachos.id_despacho"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_ordenes_servicio_folio", "ordenes_servicio", ["folio"], unique=True)
    op.create_index("ix_ordenes_servicio_cliente_id", "ordenes_servicio", ["cliente_id"], unique=False)
    op.create_index("ix_ordenes_servicio_cotizacion_id", "ordenes_servicio", ["cotizacion_id"], unique=False)
    op.create_index("ix_ordenes_servicio_flete_id", "ordenes_servicio", ["flete_id"], unique=False)
    op.create_index("ix_ordenes_servicio_viaje_id", "ordenes_servicio", ["viaje_id"], unique=False)
    op.create_index("ix_ordenes_servicio_despacho_id", "ordenes_servicio", ["despacho_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_ordenes_servicio_despacho_id", table_name="ordenes_servicio")
    op.drop_index("ix_ordenes_servicio_viaje_id", table_name="ordenes_servicio")
    op.drop_index("ix_ordenes_servicio_flete_id", table_name="ordenes_servicio")
    op.drop_index("ix_ordenes_servicio_cotizacion_id", table_name="ordenes_servicio")
    op.drop_index("ix_ordenes_servicio_cliente_id", table_name="ordenes_servicio")
    op.drop_index("ix_ordenes_servicio_folio", table_name="ordenes_servicio")
    op.drop_table("ordenes_servicio")
