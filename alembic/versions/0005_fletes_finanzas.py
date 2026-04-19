"""Extiende fletes con campos comerciales y de margen.

Revision ID: 0005_fletes_finanzas
Revises: 0004_despachos
Create Date: 2026-03-28

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0005_fletes_finanzas"
down_revision: Union[str, Sequence[str], None] = "0004_despachos"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "fletes",
        sa.Column("tipo_operacion", sa.String(length=24), server_default="subcontratado", nullable=False),
    )
    op.add_column("fletes", sa.Column("tipo_unidad", sa.String(length=64), nullable=True))
    op.add_column("fletes", sa.Column("tipo_carga", sa.String(length=64), nullable=True))
    op.add_column("fletes", sa.Column("precio_venta", sa.Numeric(precision=14, scale=2), nullable=True))
    op.add_column("fletes", sa.Column("costo_transporte_estimado", sa.Numeric(precision=14, scale=2), nullable=True))
    op.add_column("fletes", sa.Column("costo_transporte_real", sa.Numeric(precision=14, scale=2), nullable=True))
    op.add_column("fletes", sa.Column("margen_estimado", sa.Numeric(precision=14, scale=2), nullable=True))
    op.add_column("fletes", sa.Column("margen_real", sa.Numeric(precision=14, scale=2), nullable=True))
    op.add_column(
        "fletes",
        sa.Column("metodo_calculo", sa.String(length=24), server_default="manual", nullable=False),
    )

    op.execute("UPDATE fletes SET precio_venta = monto_estimado WHERE precio_venta IS NULL")
    op.alter_column("fletes", "precio_venta", existing_type=sa.Numeric(precision=14, scale=2), nullable=False)


def downgrade() -> None:
    op.drop_column("fletes", "metodo_calculo")
    op.drop_column("fletes", "margen_real")
    op.drop_column("fletes", "margen_estimado")
    op.drop_column("fletes", "costo_transporte_real")
    op.drop_column("fletes", "costo_transporte_estimado")
    op.drop_column("fletes", "precio_venta")
    op.drop_column("fletes", "tipo_carga")
    op.drop_column("fletes", "tipo_unidad")
    op.drop_column("fletes", "tipo_operacion")
