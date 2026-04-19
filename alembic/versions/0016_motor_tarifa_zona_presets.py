"""Presets motor tarifas por region y tipo de unidad.

Revision ID: 0016_motor_zona
Revises: 0015_tarifas_tipo
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0016_motor_zona"
down_revision: Union[str, Sequence[str], None] = "0015_tarifas_tipo"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "motor_tarifa_zona_presets",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("region_key", sa.String(length=64), nullable=False),
        sa.Column("tipo_unidad_norm", sa.String(length=64), nullable=False),
        sa.Column("cpk_referencia", sa.Numeric(precision=14, scale=4), nullable=False),
        sa.Column("mu_local", sa.Numeric(precision=8, scale=4), nullable=True),
        sa.Column("mu_estatal", sa.Numeric(precision=8, scale=4), nullable=True),
        sa.Column("mu_federal", sa.Numeric(precision=8, scale=4), nullable=True),
        sa.Column("notas", sa.String(length=500), nullable=True),
        sa.Column("activo", sa.Boolean(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_motor_zona_region_tipo",
        "motor_tarifa_zona_presets",
        ["region_key", "tipo_unidad_norm", "activo"],
    )

    inserts = [
        """INSERT INTO motor_tarifa_zona_presets (region_key, tipo_unidad_norm, cpk_referencia, mu_local, mu_estatal, mu_federal, notas, activo) VALUES ('veracruz_sureste', 'rabon', 19.0000, 1.2600, 1.3000, 1.3800, 'Seed referencia mercado MX', 1)""",
        """INSERT INTO motor_tarifa_zona_presets (region_key, tipo_unidad_norm, cpk_referencia, mu_local, mu_estatal, mu_federal, notas, activo) VALUES ('veracruz_sureste', 'torton', 24.0000, 1.2800, 1.3200, 1.4000, 'Seed referencia mercado MX', 1)""",
        """INSERT INTO motor_tarifa_zona_presets (region_key, tipo_unidad_norm, cpk_referencia, mu_local, mu_estatal, mu_federal, notas, activo) VALUES ('veracruz_sureste', 'tractocamion', 34.0000, 1.2800, 1.3200, 1.4000, 'Seed referencia mercado MX', 1)""",
        """INSERT INTO motor_tarifa_zona_presets (region_key, tipo_unidad_norm, cpk_referencia, mu_local, mu_estatal, mu_federal, notas, activo) VALUES ('centro', 'torton', 28.0000, 1.3000, 1.3400, 1.4200, 'Seed referencia mercado MX', 1)""",
        """INSERT INTO motor_tarifa_zona_presets (region_key, tipo_unidad_norm, cpk_referencia, mu_local, mu_estatal, mu_federal, notas, activo) VALUES ('norte', 'tractocamion', 38.0000, 1.3000, 1.3600, 1.4500, 'Seed referencia mercado MX', 1)""",
        """INSERT INTO motor_tarifa_zona_presets (region_key, tipo_unidad_norm, cpk_referencia, mu_local, mu_estatal, mu_federal, notas, activo) VALUES ('bajio', 'torton', 25.0000, 1.2800, 1.3200, 1.4000, 'Seed referencia mercado MX', 1)""",
        """INSERT INTO motor_tarifa_zona_presets (region_key, tipo_unidad_norm, cpk_referencia, mu_local, mu_estatal, mu_federal, notas, activo) VALUES ('generica', 'torton', 24.0000, NULL, NULL, NULL, 'Seed referencia mercado MX', 1)""",
    ]
    for sql in inserts:
        op.execute(sa.text(sql))


def downgrade() -> None:
    op.drop_index("ix_motor_zona_region_tipo", table_name="motor_tarifa_zona_presets")
    op.drop_table("motor_tarifa_zona_presets")
