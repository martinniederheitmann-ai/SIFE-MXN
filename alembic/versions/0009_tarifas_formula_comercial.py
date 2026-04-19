"""Enriquece tarifas de flete con ambito y formula comercial.

Revision ID: 0009_tarifas_formula_comercial
Revises: 0009_transportistas_v2
Create Date: 2026-03-28

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0009_tarifas_formula_comercial"
down_revision: Union[str, Sequence[str], None] = "0009_transportistas_v2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "tarifas_flete",
        sa.Column("ambito", sa.String(length=24), server_default="federal", nullable=False),
    )
    op.add_column(
        "tarifas_flete",
        sa.Column("modalidad_cobro", sa.String(length=24), server_default="mixta", nullable=False),
    )
    op.add_column(
        "tarifas_flete",
        sa.Column("tarifa_tonelada", sa.Numeric(precision=14, scale=4), server_default="0", nullable=False),
    )
    op.add_column(
        "tarifas_flete",
        sa.Column("tarifa_hora", sa.Numeric(precision=14, scale=2), server_default="0", nullable=False),
    )
    op.add_column(
        "tarifas_flete",
        sa.Column("tarifa_dia", sa.Numeric(precision=14, scale=2), server_default="0", nullable=False),
    )
    op.add_column(
        "tarifas_flete",
        sa.Column(
            "porcentaje_utilidad",
            sa.Numeric(precision=8, scale=4),
            server_default="0.2000",
            nullable=False,
        ),
    )
    op.add_column(
        "tarifas_flete",
        sa.Column(
            "porcentaje_riesgo",
            sa.Numeric(precision=8, scale=4),
            server_default="0",
            nullable=False,
        ),
    )
    op.add_column(
        "tarifas_flete",
        sa.Column(
            "porcentaje_urgencia",
            sa.Numeric(precision=8, scale=4),
            server_default="0",
            nullable=False,
        ),
    )
    op.add_column(
        "tarifas_flete",
        sa.Column(
            "porcentaje_retorno_vacio",
            sa.Numeric(precision=8, scale=4),
            server_default="0",
            nullable=False,
        ),
    )
    op.add_column(
        "tarifas_flete",
        sa.Column(
            "porcentaje_carga_especial",
            sa.Numeric(precision=8, scale=4),
            server_default="0",
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_column("tarifas_flete", "porcentaje_carga_especial")
    op.drop_column("tarifas_flete", "porcentaje_retorno_vacio")
    op.drop_column("tarifas_flete", "porcentaje_urgencia")
    op.drop_column("tarifas_flete", "porcentaje_riesgo")
    op.drop_column("tarifas_flete", "porcentaje_utilidad")
    op.drop_column("tarifas_flete", "tarifa_dia")
    op.drop_column("tarifas_flete", "tarifa_hora")
    op.drop_column("tarifas_flete", "tarifa_tonelada")
    op.drop_column("tarifas_flete", "modalidad_cobro")
    op.drop_column("tarifas_flete", "ambito")
