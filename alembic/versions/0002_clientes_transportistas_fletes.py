"""Tablas clientes, transportistas y fletes.

Revision ID: 0002_flete
Revises: 0001_initial_viajes
Create Date: 2025-03-24

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0002_flete"
down_revision: Union[str, Sequence[str], None] = "0001_initial_viajes"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "clientes",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("razon_social", sa.String(length=255), nullable=False),
        sa.Column("rfc", sa.String(length=20), nullable=True),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("telefono", sa.String(length=40), nullable=True),
        sa.Column("direccion", sa.Text(), nullable=True),
        sa.Column("activo", sa.Boolean(), server_default=sa.text("1"), nullable=False),
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
    op.create_index("ix_clientes_rfc", "clientes", ["rfc"], unique=False)

    op.create_table(
        "transportistas",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("nombre", sa.String(length=255), nullable=False),
        sa.Column("rfc", sa.String(length=20), nullable=True),
        sa.Column("contacto", sa.String(length=255), nullable=True),
        sa.Column("telefono", sa.String(length=40), nullable=True),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("notas", sa.Text(), nullable=True),
        sa.Column("activo", sa.Boolean(), server_default=sa.text("1"), nullable=False),
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
    op.create_index("ix_transportistas_rfc", "transportistas", ["rfc"], unique=False)

    op.create_table(
        "fletes",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("codigo_flete", sa.String(length=64), nullable=False),
        sa.Column("cliente_id", sa.Integer(), nullable=False),
        sa.Column("transportista_id", sa.Integer(), nullable=False),
        sa.Column("viaje_id", sa.Integer(), nullable=True),
        sa.Column("descripcion_carga", sa.String(length=500), nullable=True),
        sa.Column("peso_kg", sa.Numeric(precision=12, scale=3), nullable=False),
        sa.Column("volumen_m3", sa.Numeric(precision=12, scale=3), nullable=True),
        sa.Column("numero_bultos", sa.Integer(), nullable=True),
        sa.Column("distancia_km", sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column("monto_estimado", sa.Numeric(precision=14, scale=2), nullable=False),
        sa.Column("moneda", sa.String(length=3), server_default="MXN", nullable=False),
        sa.Column(
            "estado",
            sa.String(length=32),
            server_default="cotizado",
            nullable=False,
        ),
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
        sa.ForeignKeyConstraint(["cliente_id"], ["clientes.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["transportista_id"], ["transportistas.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["viaje_id"], ["viajes.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_fletes_codigo_flete", "fletes", ["codigo_flete"], unique=True)
    op.create_index("ix_fletes_cliente_id", "fletes", ["cliente_id"], unique=False)
    op.create_index("ix_fletes_transportista_id", "fletes", ["transportista_id"], unique=False)
    op.create_index("ix_fletes_viaje_id", "fletes", ["viaje_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_fletes_viaje_id", table_name="fletes")
    op.drop_index("ix_fletes_transportista_id", table_name="fletes")
    op.drop_index("ix_fletes_cliente_id", table_name="fletes")
    op.drop_index("ix_fletes_codigo_flete", table_name="fletes")
    op.drop_table("fletes")
    op.drop_index("ix_transportistas_rfc", table_name="transportistas")
    op.drop_table("transportistas")
    op.drop_index("ix_clientes_rfc", table_name="clientes")
    op.drop_table("clientes")
