"""Separar consumo promedio diesel y gasolina en operadores.

Revision ID: 0018_operador_diesel_gasolina
Revises: 0017_cumplimiento
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0018_operador_diesel_gasolina"
down_revision: Union[str, Sequence[str], None] = "0017_cumplimiento"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "operadores",
        sa.Column("consumo_diesel_promedio", sa.Numeric(precision=10, scale=2), nullable=True),
    )
    op.add_column(
        "operadores",
        sa.Column("consumo_gasolina_promedio", sa.Numeric(precision=10, scale=2), nullable=True),
    )
    op.execute(
        sa.text(
            "UPDATE operadores SET consumo_diesel_promedio = consumo_combustible_promedio "
            "WHERE consumo_combustible_promedio IS NOT NULL"
        )
    )
    op.drop_column("operadores", "consumo_combustible_promedio")


def downgrade() -> None:
    op.add_column(
        "operadores",
        sa.Column(
            "consumo_combustible_promedio",
            sa.Numeric(precision=10, scale=2),
            nullable=True,
        ),
    )
    op.execute(
        sa.text(
            "UPDATE operadores SET consumo_combustible_promedio = "
            "COALESCE(consumo_diesel_promedio, consumo_gasolina_promedio)"
        )
    )
    op.drop_column("operadores", "consumo_diesel_promedio")
    op.drop_column("operadores", "consumo_gasolina_promedio")
