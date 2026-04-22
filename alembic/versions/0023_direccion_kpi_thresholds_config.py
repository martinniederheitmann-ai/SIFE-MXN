"""Configuracion persistente de umbrales KPI de direccion.

Revision ID: 0023_direccion_kpi_thresholds_config
Revises: 0022_audit_logs_and_api_key_hardening
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0023_direccion_kpi_thresholds_config"
down_revision: Union[str, Sequence[str], None] = "0022_audit_logs_and_api_key_hardening"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "direccion_kpi_configs",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("scope_type", sa.String(length=16), nullable=False),
        sa.Column("scope_value", sa.String(length=120), nullable=False),
        sa.Column("config_json", sa.Text(), nullable=False),
        sa.Column("updated_by_user_id", sa.Integer(), nullable=True),
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
        sa.ForeignKeyConstraint(["updated_by_user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_direccion_kpi_configs_scope_type", "direccion_kpi_configs", ["scope_type"], unique=False)
    op.create_index("ix_direccion_kpi_configs_scope_value", "direccion_kpi_configs", ["scope_value"], unique=False)
    op.create_index(
        "uq_direccion_kpi_configs_scope_type_scope_value",
        "direccion_kpi_configs",
        ["scope_type", "scope_value"],
        unique=True,
    )

    op.create_table(
        "direccion_kpi_config_history",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("config_id", sa.Integer(), nullable=False),
        sa.Column("mode", sa.String(length=32), nullable=False),
        sa.Column("changes_json", sa.Text(), nullable=True),
        sa.Column("created_by_user_id", sa.Integer(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP(6)"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["config_id"], ["direccion_kpi_configs.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["created_by_user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_direccion_kpi_config_history_config_id",
        "direccion_kpi_config_history",
        ["config_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_direccion_kpi_config_history_config_id", table_name="direccion_kpi_config_history")
    op.drop_table("direccion_kpi_config_history")

    op.drop_index("uq_direccion_kpi_configs_scope_type_scope_value", table_name="direccion_kpi_configs")
    op.drop_index("ix_direccion_kpi_configs_scope_value", table_name="direccion_kpi_configs")
    op.drop_index("ix_direccion_kpi_configs_scope_type", table_name="direccion_kpi_configs")
    op.drop_table("direccion_kpi_configs")
