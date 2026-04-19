"""Repara alembic_version cuando apunta a una revisión inexistente en el repo.

Ej.: la base tiene `0017_presupuesto_gasto` (archivo ausente) y Alembic falla.

Uso:

    python scripts/fix_alembic_version.py
    python -m alembic upgrade head
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import text

from app.core.database import engine

VERSIONS_DIR = Path(__file__).resolve().parents[1] / "alembic" / "versions"
SAFE_BASE = "0016_motor_zona"


def _revision_ids_in_repo() -> set[str]:
    ids: set[str] = set()
    for path in VERSIONS_DIR.glob("*.py"):
        text_content = path.read_text(encoding="utf-8")
        m = re.search(r'^revision:\s*str\s*=\s*["\']([^"\']+)["\']', text_content, re.M)
        if m:
            ids.add(m.group(1))
    return ids


def main() -> None:
    known = _revision_ids_in_repo()
    with engine.connect() as conn:
        r = conn.execute(text("SELECT version_num FROM alembic_version LIMIT 1"))
        row = r.fetchone()
        if not row:
            print("No hay fila en alembic_version. Ejecuta: python -m alembic stamp 0016_motor_zona")
            return
        current = row[0]
        print(f"alembic_version actual: {current}")

        if current in known:
            print("La revisión existe en el repositorio; no se modifica.")
            return

        print(f"Revisión '{current}' no está en el repo. Se fija en '{SAFE_BASE}' (última base conocida antes de 0017).")
        conn.execute(text("UPDATE alembic_version SET version_num = :v"), {"v": SAFE_BASE})
        conn.commit()
        print("OK. Ejecuta: python -m alembic upgrade head")


if __name__ == "__main__":
    main()
