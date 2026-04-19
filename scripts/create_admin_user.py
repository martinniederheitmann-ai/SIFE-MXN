"""
Crea el primer usuario administrador (rol admin).

Uso (con virtualenv activado, desde la raiz del proyecto):
  python scripts/create_admin_user.py --username admin --password "TuPasswordSeguro"

Requiere: migracion 0019 aplicada, JWT_SECRET_KEY en .env (para login posterior).
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.core.security import hash_password
from app.models.role import Role
from app.models.user import User


def main() -> int:
    p = argparse.ArgumentParser(description="Alta usuario admin en SIFE-MXN")
    p.add_argument("--username", required=True)
    p.add_argument("--password", required=True)
    p.add_argument("--email", default="", help="Opcional")
    p.add_argument("--full-name", default="", dest="full_name")
    args = p.parse_args()

    db: Session = SessionLocal()
    try:
        existing = db.execute(select(User).where(User.username == args.username.strip())).scalar_one_or_none()
        if existing:
            print("Error: ya existe un usuario con ese nombre.", file=sys.stderr)
            return 1

        role = db.execute(select(Role).where(Role.name == "admin")).scalar_one_or_none()
        if role is None:
            print("Error: rol 'admin' no encontrado. Aplique migraciones: alembic upgrade head", file=sys.stderr)
            return 1

        user = User(
            username=args.username.strip(),
            email=args.email.strip() or None,
            full_name=args.full_name.strip() or None,
            hashed_password=hash_password(args.password),
            is_active=True,
            role_id=role.id,
        )
        db.add(user)
        db.commit()
        print(f"Usuario creado: id={user.id} username={user.username} rol=admin")
        return 0
    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(main())
