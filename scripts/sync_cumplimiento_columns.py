"""Añade columnas de cumplimiento documental si faltan (equivalente a migración 0017).

Preferible: `python scripts/fix_alembic_version.py` y luego `alembic upgrade head`
(con migración 0017 idempotente).

Úsalo solo si no puedes usar Alembic (sin acceso a alembic_version, etc.).
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import text

from app.core.database import engine


def _has_column(conn, table: str, column: str) -> bool:
    r = conn.execute(
        text(
            """
            SELECT COUNT(*) FROM information_schema.COLUMNS
            WHERE TABLE_SCHEMA = DATABASE()
              AND TABLE_NAME = :t
              AND COLUMN_NAME = :c
            """
        ),
        {"t": table, "c": column},
    )
    return r.scalar() > 0


def main() -> None:
    alters_fletes = [
        ("ambito_operacion", "ALTER TABLE fletes ADD COLUMN ambito_operacion VARCHAR(16) NULL"),
        ("carta_porte_uuid", "ALTER TABLE fletes ADD COLUMN carta_porte_uuid VARCHAR(64) NULL"),
        ("carta_porte_folio", "ALTER TABLE fletes ADD COLUMN carta_porte_folio VARCHAR(64) NULL"),
        ("factura_mercancia_folio", "ALTER TABLE fletes ADD COLUMN factura_mercancia_folio VARCHAR(64) NULL"),
        (
            "mercancia_documentacion_ok",
            "ALTER TABLE fletes ADD COLUMN mercancia_documentacion_ok TINYINT(1) NOT NULL DEFAULT 0",
        ),
    ]
    alters_unidades = [
        ("vigencia_seguro", "ALTER TABLE unidades ADD COLUMN vigencia_seguro DATE NULL"),
        ("vigencia_permiso_sct", "ALTER TABLE unidades ADD COLUMN vigencia_permiso_sct DATE NULL"),
        (
            "vigencia_tarjeta_circulacion",
            "ALTER TABLE unidades ADD COLUMN vigencia_tarjeta_circulacion DATE NULL",
        ),
        (
            "vigencia_verificacion_fisico_mecanica",
            "ALTER TABLE unidades ADD COLUMN vigencia_verificacion_fisico_mecanica DATE NULL",
        ),
    ]

    with engine.begin() as conn:
        for col, ddl in alters_fletes:
            if not _has_column(conn, "fletes", col):
                conn.execute(text(ddl))
                print(f"OK fletes.{col}")
            else:
                print(f"skip fletes.{col} (ya existe)")
        for col, ddl in alters_unidades:
            if not _has_column(conn, "unidades", col):
                conn.execute(text(ddl))
                print(f"OK unidades.{col}")
            else:
                print(f"skip unidades.{col} (ya existe)")

    print("Listo. Recarga /ui.")


if __name__ == "__main__":
    main()
