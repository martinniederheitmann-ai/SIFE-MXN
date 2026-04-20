"""Rol direccion (direccion general, acceso total como admin en RBAC).

Revision ID: 0020_role_direccion
Revises: 0019_users_roles
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0020_role_direccion"
down_revision: Union[str, Sequence[str], None] = "0019_users_roles"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        sa.text(
            """
            INSERT INTO roles (name, description)
            SELECT 'direccion', 'Direccion general: todos los modulos y API (mismo alcance que admin en permisos).'
            WHERE NOT EXISTS (SELECT 1 FROM roles WHERE name = 'direccion' LIMIT 1)
            """
        )
    )


def downgrade() -> None:
    op.execute(sa.text("DELETE FROM roles WHERE name = 'direccion'"))
