"""Amplia clientes con contactos, domicilios y condiciones comerciales.

Revision ID: 0008_clientes_mvp
Revises: 0007_gastos_viaje
Create Date: 2026-03-28

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0008_clientes_mvp"
down_revision: Union[str, Sequence[str], None] = "0007_gastos_viaje"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("clientes", sa.Column("nombre_comercial", sa.String(length=255), nullable=True))
    op.add_column(
        "clientes",
        sa.Column("tipo_cliente", sa.String(length=32), server_default="mixto", nullable=False),
    )
    op.add_column("clientes", sa.Column("sector", sa.String(length=120), nullable=True))
    op.add_column("clientes", sa.Column("origen_prospecto", sa.String(length=120), nullable=True))
    op.add_column("clientes", sa.Column("domicilio_fiscal", sa.Text(), nullable=True))
    op.add_column("clientes", sa.Column("sitio_web", sa.String(length=255), nullable=True))
    op.add_column("clientes", sa.Column("notas_operativas", sa.Text(), nullable=True))
    op.add_column("clientes", sa.Column("notas_comerciales", sa.Text(), nullable=True))

    op.execute(
        """
        UPDATE clientes
        SET domicilio_fiscal = direccion
        WHERE domicilio_fiscal IS NULL AND direccion IS NOT NULL
        """
    )

    op.create_table(
        "cliente_contactos",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("cliente_id", sa.Integer(), nullable=False),
        sa.Column("nombre", sa.String(length=255), nullable=False),
        sa.Column("area", sa.String(length=120), nullable=True),
        sa.Column("puesto", sa.String(length=120), nullable=True),
        sa.Column("telefono", sa.String(length=40), nullable=True),
        sa.Column("extension", sa.String(length=20), nullable=True),
        sa.Column("celular", sa.String(length=40), nullable=True),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("principal", sa.Boolean(), server_default=sa.text("0"), nullable=False),
        sa.Column("activo", sa.Boolean(), server_default=sa.text("1"), nullable=False),
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
        sa.ForeignKeyConstraint(["cliente_id"], ["clientes.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_cliente_contactos_cliente_id", "cliente_contactos", ["cliente_id"], unique=False)

    op.create_table(
        "cliente_domicilios",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("cliente_id", sa.Integer(), nullable=False),
        sa.Column("tipo_domicilio", sa.String(length=64), nullable=False),
        sa.Column("nombre_sede", sa.String(length=255), nullable=False),
        sa.Column("direccion_completa", sa.Text(), nullable=False),
        sa.Column("municipio", sa.String(length=120), nullable=True),
        sa.Column("estado", sa.String(length=120), nullable=True),
        sa.Column("codigo_postal", sa.String(length=12), nullable=True),
        sa.Column("horario_carga", sa.String(length=120), nullable=True),
        sa.Column("horario_descarga", sa.String(length=120), nullable=True),
        sa.Column("instrucciones_acceso", sa.Text(), nullable=True),
        sa.Column("activo", sa.Boolean(), server_default=sa.text("1"), nullable=False),
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
        sa.ForeignKeyConstraint(["cliente_id"], ["clientes.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_cliente_domicilios_cliente_id", "cliente_domicilios", ["cliente_id"], unique=False)
    op.create_index(
        "ix_cliente_domicilios_tipo_domicilio",
        "cliente_domicilios",
        ["tipo_domicilio"],
        unique=False,
    )

    op.create_table(
        "cliente_condiciones_comerciales",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("cliente_id", sa.Integer(), nullable=False),
        sa.Column("dias_credito", sa.Integer(), nullable=True),
        sa.Column("limite_credito", sa.Numeric(precision=14, scale=2), nullable=True),
        sa.Column("moneda_preferida", sa.String(length=3), server_default="MXN", nullable=False),
        sa.Column("forma_pago", sa.String(length=64), nullable=True),
        sa.Column("uso_cfdi", sa.String(length=64), nullable=True),
        sa.Column("requiere_oc", sa.Boolean(), server_default=sa.text("0"), nullable=False),
        sa.Column("requiere_cita", sa.Boolean(), server_default=sa.text("0"), nullable=False),
        sa.Column("bloqueado_credito", sa.Boolean(), server_default=sa.text("0"), nullable=False),
        sa.Column("observaciones_credito", sa.Text(), nullable=True),
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
        sa.ForeignKeyConstraint(["cliente_id"], ["clientes.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("cliente_id"),
    )
    op.create_index(
        "ix_cliente_condiciones_comerciales_cliente_id",
        "cliente_condiciones_comerciales",
        ["cliente_id"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_cliente_condiciones_comerciales_cliente_id",
        table_name="cliente_condiciones_comerciales",
    )
    op.drop_table("cliente_condiciones_comerciales")

    op.drop_index("ix_cliente_domicilios_tipo_domicilio", table_name="cliente_domicilios")
    op.drop_index("ix_cliente_domicilios_cliente_id", table_name="cliente_domicilios")
    op.drop_table("cliente_domicilios")

    op.drop_index("ix_cliente_contactos_cliente_id", table_name="cliente_contactos")
    op.drop_table("cliente_contactos")

    op.drop_column("clientes", "notas_comerciales")
    op.drop_column("clientes", "notas_operativas")
    op.drop_column("clientes", "sitio_web")
    op.drop_column("clientes", "domicilio_fiscal")
    op.drop_column("clientes", "origen_prospecto")
    op.drop_column("clientes", "sector")
    op.drop_column("clientes", "tipo_cliente")
    op.drop_column("clientes", "nombre_comercial")
