"""Tablas despachos y eventos de despacho.

Revision ID: 0004_despachos
Revises: 0003_operadores
Create Date: 2026-03-25

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0004_despachos"
down_revision: Union[str, Sequence[str], None] = "0003_operadores"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "despachos",
        sa.Column("id_despacho", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("id_asignacion", sa.Integer(), nullable=False),
        sa.Column("id_flete", sa.Integer(), nullable=True),
        sa.Column("estatus", sa.String(length=24), server_default="programado", nullable=False),
        sa.Column("salida_programada", sa.DateTime(timezone=True), nullable=True),
        sa.Column("salida_real", sa.DateTime(timezone=True), nullable=True),
        sa.Column("fecha_entrega", sa.DateTime(timezone=True), nullable=True),
        sa.Column("llegada_real", sa.DateTime(timezone=True), nullable=True),
        sa.Column("km_salida", sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column("km_llegada", sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column("evidencia_entrega", sa.String(length=1024), nullable=True),
        sa.Column("firma_recibe", sa.String(length=255), nullable=True),
        sa.Column("observaciones_salida", sa.Text(), nullable=True),
        sa.Column("observaciones_transito", sa.Text(), nullable=True),
        sa.Column("observaciones_entrega", sa.Text(), nullable=True),
        sa.Column("observaciones_cierre", sa.Text(), nullable=True),
        sa.Column("motivo_cancelacion", sa.Text(), nullable=True),
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
        sa.ForeignKeyConstraint(["id_asignacion"], ["asignaciones.id_asignacion"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["id_flete"], ["fletes.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id_despacho"),
    )
    op.create_index("ix_despachos_id_asignacion", "despachos", ["id_asignacion"], unique=True)
    op.create_index("ix_despachos_id_flete", "despachos", ["id_flete"], unique=False)

    op.create_table(
        "despacho_eventos",
        sa.Column("id_evento", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("id_despacho", sa.Integer(), nullable=False),
        sa.Column("tipo_evento", sa.String(length=24), nullable=False),
        sa.Column("fecha_evento", sa.DateTime(timezone=True), nullable=False),
        sa.Column("ubicacion", sa.String(length=255), nullable=True),
        sa.Column("descripcion", sa.Text(), nullable=False),
        sa.Column("latitud", sa.Numeric(precision=10, scale=7), nullable=True),
        sa.Column("longitud", sa.Numeric(precision=10, scale=7), nullable=True),
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
        sa.ForeignKeyConstraint(["id_despacho"], ["despachos.id_despacho"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id_evento"),
    )
    op.create_index("ix_despacho_eventos_id_despacho", "despacho_eventos", ["id_despacho"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_despacho_eventos_id_despacho", table_name="despacho_eventos")
    op.drop_table("despacho_eventos")

    op.drop_index("ix_despachos_id_flete", table_name="despachos")
    op.drop_index("ix_despachos_id_asignacion", table_name="despachos")
    op.drop_table("despachos")
