from __future__ import annotations

import sys
from logging.config import fileConfig
from pathlib import Path

from alembic import context
from alembic.ddl import impl as alembic_ddl_impl
from alembic.ddl.mysql import MySQLImpl
from sqlalchemy import Column, MetaData, PrimaryKeyConstraint, String, Table
from sqlalchemy import create_engine, pool

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.core.config import settings  # noqa: E402
from app.models import (  # noqa: E402, F401
    Asignacion,
    AuditLog,
    Base,
    Cliente,
    ClienteCondicionComercial,
    ClienteContacto,
    ClienteDomicilio,
    ClienteTarifaEspecial,
    CotizacionFlete,
    Despacho,
    DespachoEvento,
    DireccionAccion,
    DireccionIncidencia,
    DocumentoOperador,
    Factura,
    Flete,
    GastoViaje,
    IncidenteOperador,
    MotorTarifaZonaPreset,
    OrdenServicio,
    Operador,
    OperadorLaboral,
    PagoOperador,
    TarifaCompraTransportista,
    TarifaFlete,
    Transportista,
    TransportistaContacto,
    TransportistaDocumento,
    Unidad,
    Viaje,
)

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

config.set_main_option("sqlalchemy.url", settings.database_url)

target_metadata = Base.metadata


class MySQLImplVersion128(MySQLImpl):
    """Alembic por defecto usa VARCHAR(32); revisiones largas se truncan y rompen migraciones."""

    def version_table_impl(
        self,
        *,
        version_table: str,
        version_table_schema,
        version_table_pk: bool,
        **kw,
    ) -> Table:
        vt = Table(
            version_table,
            MetaData(),
            Column("version_num", String(128), nullable=False),
            schema=version_table_schema,
        )
        if version_table_pk:
            vt.append_constraint(
                PrimaryKeyConstraint("version_num", name=f"{version_table}_pkc")
            )
        return vt


class MariaDBImplVersion128(MySQLImplVersion128):
    __dialect__ = "mariadb"


alembic_ddl_impl._impls["mysql"] = MySQLImplVersion128
alembic_ddl_impl._impls["mariadb"] = MariaDBImplVersion128


def run_migrations_offline() -> None:
    url = settings.database_url
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = create_engine(settings.database_url, poolclass=pool.NullPool)

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
