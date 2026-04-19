"""
Inserta una unidad de ejemplo si hay al menos un transportista en la base.

Uso (raíz del proyecto, venv activado):
    python scripts/seed_unidad_ejemplo.py

Si devuelve "Sin transportistas", cree primero un transportista en el panel o por API.
"""

from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.core.database import SessionLocal
from app.crud import transportista as crud_transportista
from app.crud import unidad as crud_unidad
from app.schemas.unidad import UnidadCreate


def main() -> None:
    db = SessionLocal()
    try:
        rows, total = crud_transportista.list_transportistas(db, skip=0, limit=1)
        if total == 0 or not rows:
            print("Sin transportistas: cree uno antes (panel o POST /api/v1/transportistas).")
            return
        tid = rows[0].id
        economico = "DEMO-ECON-001"
        if crud_unidad.get_by_economico(db, economico):
            print(f"Ya existe unidad con economico {economico!r}. Listado OK.")
            return
        u = crud_unidad.create(
            db,
            UnidadCreate(
                transportista_id=tid,
                economico=economico,
                placas="XX-00-00",
                tipo_propiedad="propia",
                estatus_documental="vigente",
                descripcion="Unidad de ejemplo (script seed_unidad_ejemplo)",
                activo=True,
                vigencia_permiso_sct=date(2027, 12, 31),
                vigencia_seguro=date(2026, 12, 31),
            ),
        )
        print(f"Unidad creada: id_unidad={u.id_unidad}, economico={u.economico!r}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
