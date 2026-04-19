"""Tarifas: tipo operacion (venta) y tipo transportista (compra).

Revision ID: 0015_tarifas_tipo
Revises: 0014_facturas_admin
Create Date: 2026-04-03

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0015_tarifas_tipo"
down_revision: Union[str, Sequence[str], None] = "0014_facturas_admin"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "tarifas_flete",
        sa.Column(
            "tipo_operacion",
            sa.String(length=32),
            server_default="subcontratado",
            nullable=False,
        ),
    )
    op.add_column(
        "tarifas_compra_transportista",
        sa.Column(
            "tipo_transportista",
            sa.String(length=32),
            server_default="subcontratado",
            nullable=False,
        ),
    )
    conn = op.get_bind()
    conn.execute(
        sa.text(
            """
            UPDATE tarifas_compra_transportista AS t
            INNER JOIN transportistas AS tr ON t.transportista_id = tr.id
            SET t.tipo_transportista = tr.tipo_transportista
            """
        )
    )


def downgrade() -> None:
    op.drop_column("tarifas_compra_transportista", "tipo_transportista")
    op.drop_column("tarifas_flete", "tipo_operacion")
