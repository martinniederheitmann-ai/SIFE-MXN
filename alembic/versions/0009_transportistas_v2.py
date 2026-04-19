"""Amplia transportistas y enlaza unidades/operadores.

Revision ID: 0009_transportistas_v2
Revises: 0008_clientes_mvp
Create Date: 2026-04-01

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0009_transportistas_v2"
down_revision: Union[str, Sequence[str], None] = "0008_clientes_mvp"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "transportistas",
        sa.Column("tipo_transportista", sa.String(length=32), server_default="subcontratado", nullable=False),
    )
    op.add_column(
        "transportistas",
        sa.Column("tipo_persona", sa.String(length=16), server_default="moral", nullable=False),
    )
    op.add_column("transportistas", sa.Column("nombre_comercial", sa.String(length=255), nullable=True))
    op.add_column("transportistas", sa.Column("curp", sa.String(length=18), nullable=True))
    op.create_index("ix_transportistas_curp", "transportistas", ["curp"], unique=False)
    op.add_column("transportistas", sa.Column("regimen_fiscal", sa.String(length=64), nullable=True))
    op.add_column("transportistas", sa.Column("fecha_alta", sa.Date(), nullable=True))
    op.add_column(
        "transportistas",
        sa.Column("estatus", sa.String(length=16), server_default="activo", nullable=False),
    )
    op.add_column("transportistas", sa.Column("telefono_general", sa.String(length=40), nullable=True))
    op.add_column("transportistas", sa.Column("email_general", sa.String(length=255), nullable=True))
    op.add_column("transportistas", sa.Column("sitio_web", sa.String(length=255), nullable=True))
    op.add_column("transportistas", sa.Column("direccion_fiscal", sa.Text(), nullable=True))
    op.add_column("transportistas", sa.Column("direccion_operativa", sa.Text(), nullable=True))
    op.add_column("transportistas", sa.Column("ciudad", sa.String(length=120), nullable=True))
    op.add_column("transportistas", sa.Column("estado", sa.String(length=120), nullable=True))
    op.add_column("transportistas", sa.Column("pais", sa.String(length=120), nullable=True))
    op.add_column("transportistas", sa.Column("codigo_postal", sa.String(length=12), nullable=True))
    op.add_column(
        "transportistas",
        sa.Column("nivel_confianza", sa.String(length=16), server_default="medio", nullable=False),
    )
    op.add_column(
        "transportistas",
        sa.Column("blacklist", sa.Boolean(), server_default=sa.text("0"), nullable=False),
    )
    op.add_column(
        "transportistas",
        sa.Column("prioridad_asignacion", sa.Integer(), server_default="0", nullable=False),
    )
    op.add_column("transportistas", sa.Column("notas_operativas", sa.Text(), nullable=True))
    op.add_column("transportistas", sa.Column("notas_comerciales", sa.Text(), nullable=True))

    op.execute("UPDATE transportistas SET fecha_alta = CURRENT_DATE() WHERE fecha_alta IS NULL")
    op.execute(
        """
        UPDATE transportistas
        SET telefono_general = telefono
        WHERE telefono_general IS NULL AND telefono IS NOT NULL
        """
    )
    op.execute(
        """
        UPDATE transportistas
        SET email_general = email
        WHERE email_general IS NULL AND email IS NOT NULL
        """
    )
    op.execute(
        """
        UPDATE transportistas
        SET notas_operativas = notas
        WHERE notas_operativas IS NULL AND notas IS NOT NULL
        """
    )

    op.create_table(
        "transportista_contactos",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("transportista_id", sa.Integer(), nullable=False),
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
        sa.ForeignKeyConstraint(["transportista_id"], ["transportistas.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_transportista_contactos_transportista_id",
        "transportista_contactos",
        ["transportista_id"],
        unique=False,
    )

    op.create_table(
        "transportista_documentos",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("transportista_id", sa.Integer(), nullable=False),
        sa.Column("tipo_documento", sa.String(length=32), nullable=False),
        sa.Column("numero_documento", sa.String(length=120), nullable=True),
        sa.Column("fecha_emision", sa.Date(), nullable=True),
        sa.Column("fecha_vencimiento", sa.Date(), nullable=True),
        sa.Column("archivo_url", sa.String(length=1024), nullable=True),
        sa.Column("estatus", sa.String(length=16), server_default="pendiente", nullable=False),
        sa.Column("observaciones", sa.Text(), nullable=True),
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
        sa.ForeignKeyConstraint(["transportista_id"], ["transportistas.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_transportista_documentos_transportista_id",
        "transportista_documentos",
        ["transportista_id"],
        unique=False,
    )

    op.add_column("unidades", sa.Column("transportista_id", sa.Integer(), nullable=True))
    op.create_index("ix_unidades_transportista_id", "unidades", ["transportista_id"], unique=False)
    op.create_foreign_key(
        "fk_unidades_transportista_id",
        "unidades",
        "transportistas",
        ["transportista_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.add_column("unidades", sa.Column("tipo_propiedad", sa.String(length=32), nullable=True))
    op.add_column("unidades", sa.Column("estatus_documental", sa.String(length=32), nullable=True))

    op.add_column("operadores", sa.Column("transportista_id", sa.Integer(), nullable=True))
    op.create_index("ix_operadores_transportista_id", "operadores", ["transportista_id"], unique=False)
    op.create_foreign_key(
        "fk_operadores_transportista_id",
        "operadores",
        "transportistas",
        ["transportista_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.add_column("operadores", sa.Column("tipo_contratacion", sa.String(length=32), nullable=True))
    op.add_column("operadores", sa.Column("licencia", sa.String(length=64), nullable=True))
    op.add_column("operadores", sa.Column("tipo_licencia", sa.String(length=32), nullable=True))
    op.add_column("operadores", sa.Column("vigencia_licencia", sa.Date(), nullable=True))
    op.add_column("operadores", sa.Column("estatus_documental", sa.String(length=32), nullable=True))


def downgrade() -> None:
    op.drop_column("operadores", "estatus_documental")
    op.drop_column("operadores", "vigencia_licencia")
    op.drop_column("operadores", "tipo_licencia")
    op.drop_column("operadores", "licencia")
    op.drop_column("operadores", "tipo_contratacion")
    op.drop_constraint("fk_operadores_transportista_id", "operadores", type_="foreignkey")
    op.drop_index("ix_operadores_transportista_id", table_name="operadores")
    op.drop_column("operadores", "transportista_id")

    op.drop_column("unidades", "estatus_documental")
    op.drop_column("unidades", "tipo_propiedad")
    op.drop_constraint("fk_unidades_transportista_id", "unidades", type_="foreignkey")
    op.drop_index("ix_unidades_transportista_id", table_name="unidades")
    op.drop_column("unidades", "transportista_id")

    op.drop_index("ix_transportista_documentos_transportista_id", table_name="transportista_documentos")
    op.drop_table("transportista_documentos")

    op.drop_index("ix_transportista_contactos_transportista_id", table_name="transportista_contactos")
    op.drop_table("transportista_contactos")

    op.drop_column("transportistas", "notas_comerciales")
    op.drop_column("transportistas", "notas_operativas")
    op.drop_column("transportistas", "prioridad_asignacion")
    op.drop_column("transportistas", "blacklist")
    op.drop_column("transportistas", "nivel_confianza")
    op.drop_column("transportistas", "codigo_postal")
    op.drop_column("transportistas", "pais")
    op.drop_column("transportistas", "estado")
    op.drop_column("transportistas", "ciudad")
    op.drop_column("transportistas", "direccion_operativa")
    op.drop_column("transportistas", "direccion_fiscal")
    op.drop_column("transportistas", "sitio_web")
    op.drop_column("transportistas", "email_general")
    op.drop_column("transportistas", "telefono_general")
    op.drop_column("transportistas", "estatus")
    op.drop_column("transportistas", "fecha_alta")
    op.drop_column("transportistas", "regimen_fiscal")
    op.drop_index("ix_transportistas_curp", table_name="transportistas")
    op.drop_column("transportistas", "curp")
    op.drop_column("transportistas", "nombre_comercial")
    op.drop_column("transportistas", "tipo_persona")
    op.drop_column("transportistas", "tipo_transportista")
