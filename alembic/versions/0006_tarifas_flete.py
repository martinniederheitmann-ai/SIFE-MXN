"""Crea catalogo de tarifas de flete.

Revision ID: 0006_tarifas_flete
Revises: 0005_fletes_finanzas
Create Date: 2026-03-28

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0006_tarifas_flete"
down_revision: Union[str, Sequence[str], None] = "0005_fletes_finanzas"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "tarifas_flete",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("nombre_tarifa", sa.String(length=120), nullable=False),
        sa.Column("origen", sa.String(length=255), nullable=False),
        sa.Column("destino", sa.String(length=255), nullable=False),
        sa.Column("tipo_unidad", sa.String(length=64), nullable=False),
        sa.Column("tipo_carga", sa.String(length=64), nullable=True),
        sa.Column("tarifa_base", sa.Numeric(precision=14, scale=2), nullable=False),
        sa.Column("tarifa_km", sa.Numeric(precision=14, scale=4), server_default="0", nullable=False),
        sa.Column("tarifa_kg", sa.Numeric(precision=14, scale=6), server_default="0", nullable=False),
        sa.Column("recargo_minimo", sa.Numeric(precision=14, scale=2), server_default="0", nullable=False),
        sa.Column("moneda", sa.String(length=3), server_default="MXN", nullable=False),
        sa.Column("activo", sa.Boolean(), server_default=sa.text("1"), nullable=False),
        sa.Column("vigencia_inicio", sa.Date(), nullable=True),
        sa.Column("vigencia_fin", sa.Date(), nullable=True),
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
    op.create_index("ix_tarifas_flete_nombre_tarifa", "tarifas_flete", ["nombre_tarifa"], unique=False)
    op.create_index("ix_tarifas_flete_origen", "tarifas_flete", ["origen"], unique=False)
    op.create_index("ix_tarifas_flete_destino", "tarifas_flete", ["destino"], unique=False)
    op.create_index("ix_tarifas_flete_tipo_unidad", "tarifas_flete", ["tipo_unidad"], unique=False)
    op.create_index("ix_tarifas_flete_tipo_carga", "tarifas_flete", ["tipo_carga"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_tarifas_flete_tipo_carga", table_name="tarifas_flete")
    op.drop_index("ix_tarifas_flete_tipo_unidad", table_name="tarifas_flete")
    op.drop_index("ix_tarifas_flete_destino", table_name="tarifas_flete")
    op.drop_index("ix_tarifas_flete_origen", table_name="tarifas_flete")
    op.drop_index("ix_tarifas_flete_nombre_tarifa", table_name="tarifas_flete")
    op.drop_table("tarifas_flete")
