"""Usuarios y roles para autenticacion JWT.

Revision ID: 0019_users_roles
Revises: 0018_operador_diesel_gasolina
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0019_users_roles"
down_revision: Union[str, Sequence[str], None] = "0018_operador_diesel_gasolina"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "roles",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=64), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name", name="uq_roles_name"),
    )
    op.create_index("ix_roles_name", "roles", ["name"], unique=False)

    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("username", sa.String(length=80), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("full_name", sa.String(length=255), nullable=True),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default="1", nullable=False),
        sa.Column("role_id", sa.Integer(), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
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
        sa.ForeignKeyConstraint(["role_id"], ["roles.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("username", name="uq_users_username"),
    )
    op.create_index("ix_users_username", "users", ["username"], unique=False)

    roles = [
        ("admin", "Acceso total y administracion de usuarios (futuro)."),
        ("operaciones", "Viajes, fletes, despachos, asignaciones."),
        ("contabilidad", "Facturas, gastos, reportes financieros."),
        ("ventas", "Clientes, cotizaciones, condiciones comerciales."),
        ("consulta", "Solo lectura en modulos permitidos."),
    ]
    for name, desc in roles:
        op.execute(
            sa.text("INSERT INTO roles (name, description) VALUES (:n, :d)").bindparams(
                n=name, d=desc
            )
        )


def downgrade() -> None:
    op.drop_index("ix_users_username", table_name="users")
    op.drop_table("users")
    op.drop_index("ix_roles_name", table_name="roles")
    op.drop_table("roles")
