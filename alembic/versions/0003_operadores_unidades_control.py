"""Tablas operadores, unidades y control operativo.

Revision ID: 0003_operadores
Revises: 0002_flete
Create Date: 2026-03-25

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0003_operadores"
down_revision: Union[str, Sequence[str], None] = "0002_flete"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "unidades",
        sa.Column("id_unidad", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("economico", sa.String(length=64), nullable=False),
        sa.Column("placas", sa.String(length=20), nullable=True),
        sa.Column("descripcion", sa.String(length=255), nullable=True),
        sa.Column("detalle", sa.Text(), nullable=True),
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
        sa.PrimaryKeyConstraint("id_unidad"),
    )
    op.create_index("ix_unidades_economico", "unidades", ["economico"], unique=True)
    op.create_index("ix_unidades_placas", "unidades", ["placas"], unique=False)

    op.create_table(
        "operadores",
        sa.Column("id_operador", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("nombre", sa.String(length=100), nullable=False),
        sa.Column("apellido_paterno", sa.String(length=100), nullable=False),
        sa.Column("apellido_materno", sa.String(length=100), nullable=True),
        sa.Column("fecha_nacimiento", sa.Date(), nullable=False),
        sa.Column("curp", sa.String(length=18), nullable=False),
        sa.Column("rfc", sa.String(length=13), nullable=False),
        sa.Column("nss", sa.String(length=11), nullable=False),
        sa.Column("estado_civil", sa.String(length=32), nullable=False),
        sa.Column("tipo_sangre", sa.String(length=8), nullable=False),
        sa.Column("fotografia", sa.String(length=1024), nullable=True),
        sa.Column("telefono_principal", sa.String(length=20), nullable=False),
        sa.Column("telefono_emergencia", sa.String(length=20), nullable=True),
        sa.Column("nombre_contacto_emergencia", sa.String(length=255), nullable=True),
        sa.Column("direccion", sa.String(length=255), nullable=False),
        sa.Column("colonia", sa.String(length=120), nullable=False),
        sa.Column("municipio", sa.String(length=120), nullable=False),
        sa.Column(
            "estado_geografico",
            sa.String(length=64),
            nullable=False,
            comment="Entidad federativa (campo 'estado' del domicilio)",
        ),
        sa.Column("codigo_postal", sa.String(length=5), nullable=False),
        sa.Column("correo_electronico", sa.String(length=255), nullable=False),
        sa.Column("anios_experiencia", sa.Integer(), nullable=True),
        sa.Column("tipos_unidad_manejadas", sa.JSON(), nullable=True),
        sa.Column("rutas_conocidas", sa.Text(), nullable=True),
        sa.Column("tipos_carga_experiencia", sa.JSON(), nullable=True),
        sa.Column("certificaciones", sa.Text(), nullable=True),
        sa.Column("ultima_revision_medica", sa.Date(), nullable=True),
        sa.Column("resultado_apto", sa.Boolean(), nullable=True),
        sa.Column("restricciones_medicas", sa.Text(), nullable=True),
        sa.Column("proxima_revision_medica", sa.Date(), nullable=True),
        sa.Column("puntualidad", sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column(
            "consumo_combustible_promedio",
            sa.Numeric(precision=10, scale=2),
            nullable=True,
        ),
        sa.Column("incidencias_desempeno", sa.Text(), nullable=True),
        sa.Column("calificacion_general", sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column("comentarios_desempeno", sa.Text(), nullable=True),
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
        sa.PrimaryKeyConstraint("id_operador"),
    )
    op.create_index("ix_operadores_curp", "operadores", ["curp"], unique=True)
    op.create_index("ix_operadores_nss", "operadores", ["nss"], unique=True)
    op.create_index("ix_operadores_rfc", "operadores", ["rfc"], unique=False)

    op.create_table(
        "documentos_operador",
        sa.Column("id_documento", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("id_operador", sa.Integer(), nullable=False),
        sa.Column("tipo_documento", sa.String(length=48), nullable=False),
        sa.Column("numero_documento", sa.String(length=120), nullable=True),
        sa.Column("fecha_expedicion", sa.Date(), nullable=True),
        sa.Column("fecha_vencimiento", sa.Date(), nullable=True),
        sa.Column("archivo", sa.String(length=1024), nullable=True),
        sa.Column("estatus", sa.String(length=16), server_default="vigente", nullable=False),
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
        sa.ForeignKeyConstraint(["id_operador"], ["operadores.id_operador"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id_documento"),
    )
    op.create_index("ix_documentos_operador_id_operador", "documentos_operador", ["id_operador"], unique=False)

    op.create_table(
        "operador_laboral",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("id_operador", sa.Integer(), nullable=False),
        sa.Column("fecha_ingreso", sa.Date(), nullable=False),
        sa.Column("tipo_contrato", sa.String(length=24), nullable=False),
        sa.Column("puesto", sa.String(length=32), nullable=False),
        sa.Column("salario_base", sa.Numeric(precision=14, scale=2), nullable=False),
        sa.Column("tipo_pago", sa.String(length=24), nullable=False),
        sa.Column("estatus", sa.String(length=24), server_default="activo", nullable=False),
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
        sa.ForeignKeyConstraint(["id_operador"], ["operadores.id_operador"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_operador_laboral_id_operador", "operador_laboral", ["id_operador"], unique=True)

    op.create_table(
        "incidentes_operador",
        sa.Column("id_incidente", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("id_operador", sa.Integer(), nullable=False),
        sa.Column("tipo", sa.String(length=24), nullable=False),
        sa.Column("fecha", sa.Date(), nullable=False),
        sa.Column("descripcion", sa.Text(), nullable=False),
        sa.Column("costo_estimado", sa.Numeric(precision=14, scale=2), nullable=True),
        sa.Column("resolucion", sa.Text(), nullable=True),
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
        sa.ForeignKeyConstraint(["id_operador"], ["operadores.id_operador"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id_incidente"),
    )
    op.create_index("ix_incidentes_operador_fecha", "incidentes_operador", ["fecha"], unique=False)
    op.create_index("ix_incidentes_operador_id_operador", "incidentes_operador", ["id_operador"], unique=False)

    op.create_table(
        "pagos_operador",
        sa.Column("id_pago", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("id_operador", sa.Integer(), nullable=False),
        sa.Column("tipo_pago", sa.String(length=24), nullable=False),
        sa.Column("monto", sa.Numeric(precision=14, scale=2), nullable=False),
        sa.Column("fecha", sa.Date(), nullable=False),
        sa.Column("concepto", sa.String(length=500), nullable=True),
        sa.Column("estatus", sa.String(length=16), server_default="pendiente", nullable=False),
        sa.Column("notas", sa.Text(), nullable=True),
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
        sa.ForeignKeyConstraint(["id_operador"], ["operadores.id_operador"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id_pago"),
    )
    op.create_index("ix_pagos_operador_fecha", "pagos_operador", ["fecha"], unique=False)
    op.create_index("ix_pagos_operador_id_operador", "pagos_operador", ["id_operador"], unique=False)

    op.create_table(
        "asignaciones",
        sa.Column("id_asignacion", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("id_operador", sa.Integer(), nullable=False),
        sa.Column("id_unidad", sa.Integer(), nullable=False),
        sa.Column("id_viaje", sa.Integer(), nullable=False),
        sa.Column("fecha_salida", sa.DateTime(timezone=True), nullable=False),
        sa.Column("fecha_regreso", sa.DateTime(timezone=True), nullable=True),
        sa.Column("km_inicial", sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column("km_final", sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column(
            "rendimiento_combustible",
            sa.Numeric(precision=10, scale=3),
            nullable=True,
            comment="Ej. km/L o L/100km segun politica interna",
        ),
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
        sa.ForeignKeyConstraint(["id_operador"], ["operadores.id_operador"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["id_unidad"], ["unidades.id_unidad"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["id_viaje"], ["viajes.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id_asignacion"),
    )
    op.create_index("ix_asignaciones_id_operador", "asignaciones", ["id_operador"], unique=False)
    op.create_index("ix_asignaciones_id_unidad", "asignaciones", ["id_unidad"], unique=False)
    op.create_index("ix_asignaciones_id_viaje", "asignaciones", ["id_viaje"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_asignaciones_id_viaje", table_name="asignaciones")
    op.drop_index("ix_asignaciones_id_unidad", table_name="asignaciones")
    op.drop_index("ix_asignaciones_id_operador", table_name="asignaciones")
    op.drop_table("asignaciones")

    op.drop_index("ix_pagos_operador_id_operador", table_name="pagos_operador")
    op.drop_index("ix_pagos_operador_fecha", table_name="pagos_operador")
    op.drop_table("pagos_operador")

    op.drop_index("ix_incidentes_operador_id_operador", table_name="incidentes_operador")
    op.drop_index("ix_incidentes_operador_fecha", table_name="incidentes_operador")
    op.drop_table("incidentes_operador")

    op.drop_index("ix_operador_laboral_id_operador", table_name="operador_laboral")
    op.drop_table("operador_laboral")

    op.drop_index("ix_documentos_operador_id_operador", table_name="documentos_operador")
    op.drop_table("documentos_operador")

    op.drop_index("ix_operadores_rfc", table_name="operadores")
    op.drop_index("ix_operadores_nss", table_name="operadores")
    op.drop_index("ix_operadores_curp", table_name="operadores")
    op.drop_table("operadores")

    op.drop_index("ix_unidades_placas", table_name="unidades")
    op.drop_index("ix_unidades_economico", table_name="unidades")
    op.drop_table("unidades")
