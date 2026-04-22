"""Snapshots semanales del reporte integral de direccion (comite).

Revision ID: 0024_direccion_semanal_reporte_snapshots
Revises: 0023_direccion_kpi_thresholds_config
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0024_direccion_semanal_reporte_snapshots"
down_revision: Union[str, Sequence[str], None] = "0023_direccion_kpi_thresholds_config"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "direccion_semanal_reporte_snapshots",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("week_start", sa.Date(), nullable=False),
        sa.Column("week_end", sa.Date(), nullable=False),
        sa.Column("payload_json", sa.Text(), nullable=False),
        sa.Column("created_by_user_id", sa.Integer(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP(6)"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["created_by_user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_direccion_semanal_reporte_snapshots_week_start",
        "direccion_semanal_reporte_snapshots",
        ["week_start"],
        unique=True,
    )
    op.create_index(
        "ix_direccion_semanal_reporte_snapshots_week_end",
        "direccion_semanal_reporte_snapshots",
        ["week_end"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_direccion_semanal_reporte_snapshots_week_end", table_name="direccion_semanal_reporte_snapshots")
    op.drop_index("ix_direccion_semanal_reporte_snapshots_week_start", table_name="direccion_semanal_reporte_snapshots")
    op.drop_table("direccion_semanal_reporte_snapshots")
