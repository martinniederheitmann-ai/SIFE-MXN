"""Campos de cumplimiento documental (flete, unidad).

Revision ID: 0017_cumplimiento
Revises: 0016_motor_zona
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0017_cumplimiento"
down_revision: Union[str, Sequence[str], None] = "0016_motor_zona"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _column_exists(bind, table: str, column: str) -> bool:
    r = bind.execute(
        sa.text(
            """
            SELECT COUNT(*) FROM information_schema.COLUMNS
            WHERE TABLE_SCHEMA = DATABASE()
              AND TABLE_NAME = :t
              AND COLUMN_NAME = :c
            """
        ),
        {"t": table, "c": column},
    )
    return (r.scalar() or 0) > 0


def upgrade() -> None:
    bind = op.get_bind()
    if not _column_exists(bind, "fletes", "ambito_operacion"):
        op.add_column(
            "fletes",
            sa.Column("ambito_operacion", sa.String(length=16), nullable=True),
        )
    if not _column_exists(bind, "fletes", "carta_porte_uuid"):
        op.add_column(
            "fletes",
            sa.Column("carta_porte_uuid", sa.String(length=64), nullable=True),
        )
    if not _column_exists(bind, "fletes", "carta_porte_folio"):
        op.add_column(
            "fletes",
            sa.Column("carta_porte_folio", sa.String(length=64), nullable=True),
        )
    if not _column_exists(bind, "fletes", "factura_mercancia_folio"):
        op.add_column(
            "fletes",
            sa.Column("factura_mercancia_folio", sa.String(length=64), nullable=True),
        )
    if not _column_exists(bind, "fletes", "mercancia_documentacion_ok"):
        op.add_column(
            "fletes",
            sa.Column(
                "mercancia_documentacion_ok",
                sa.Boolean(),
                nullable=False,
                server_default="0",
            ),
        )
    if not _column_exists(bind, "unidades", "vigencia_seguro"):
        op.add_column("unidades", sa.Column("vigencia_seguro", sa.Date(), nullable=True))
    if not _column_exists(bind, "unidades", "vigencia_permiso_sct"):
        op.add_column("unidades", sa.Column("vigencia_permiso_sct", sa.Date(), nullable=True))
    if not _column_exists(bind, "unidades", "vigencia_tarjeta_circulacion"):
        op.add_column(
            "unidades", sa.Column("vigencia_tarjeta_circulacion", sa.Date(), nullable=True)
        )
    if not _column_exists(bind, "unidades", "vigencia_verificacion_fisico_mecanica"):
        op.add_column(
            "unidades",
            sa.Column("vigencia_verificacion_fisico_mecanica", sa.Date(), nullable=True),
        )


def downgrade() -> None:
    bind = op.get_bind()
    for table, col in [
        ("unidades", "vigencia_verificacion_fisico_mecanica"),
        ("unidades", "vigencia_tarjeta_circulacion"),
        ("unidades", "vigencia_permiso_sct"),
        ("unidades", "vigencia_seguro"),
        ("fletes", "mercancia_documentacion_ok"),
        ("fletes", "factura_mercancia_folio"),
        ("fletes", "carta_porte_folio"),
        ("fletes", "carta_porte_uuid"),
        ("fletes", "ambito_operacion"),
    ]:
        if _column_exists(bind, table, col):
            op.drop_column(table, col)
