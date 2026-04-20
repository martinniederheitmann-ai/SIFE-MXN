"""
Crea o actualiza un usuario con el rol indicado (por defecto admin).

Uso (virtualenv activado, raiz del proyecto):
  python scripts/create_admin_user.py --username admin --password "TuPasswordSeguro"
  python scripts/create_admin_user.py --username jdoe --password "Clave123" --role operaciones

Si el usuario ya existe y quieres cambiar contraseña (y opcionalmente rol):
  python scripts/create_admin_user.py --username admin --password "NuevaClave" --reset
  python scripts/create_admin_user.py --username jdoe --password "X" --reset --role contabilidad

Requiere migraciones aplicadas y JWT_SECRET_KEY en .env para login JWT posterior.
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
    p = argparse.ArgumentParser(description="Alta o reset de usuario SIFE-MXN")
    p.add_argument("--username", required=True)
    p.add_argument("--password", required=True)
    p.add_argument(
        "--role",
        default="admin",
        help="Nombre del rol en BD: admin, direccion, operaciones, contabilidad, ventas, consulta",
    )
    p.add_argument("--email", default="", help="Opcional")
    p.add_argument("--full-name", default="", dest="full_name")
    p.add_argument(
        "--reset",
        action="store_true",
        help="Si el usuario ya existe, actualizar contraseña (y rol con --role).",
    )
    args = p.parse_args()

    db: Session = SessionLocal()
    try:
        role_name = args.role.strip()
        role = db.execute(select(Role).where(Role.name == role_name)).scalar_one_or_none()
        if role is None:
            print(
                f"Error: rol '{role_name}' no encontrado. Aplique migraciones o use un rol valido.",
                file=sys.stderr,
            )
            return 1

        existing = db.execute(select(User).where(User.username == args.username.strip())).scalar_one_or_none()
        if existing:
            if not args.reset:
                print("Error: ya existe un usuario con ese nombre. Use --reset.", file=sys.stderr)
                return 1
            existing.hashed_password = hash_password(args.password)
            existing.role_id = role.id
            if args.email.strip():
                existing.email = args.email.strip()
            if args.full_name.strip():
                existing.full_name = args.full_name.strip()
            existing.is_active = True
            db.commit()
            print(
                f"Usuario actualizado: id={existing.id} username={existing.username} rol={role_name}",
            )
            return 0

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
        print(f"Usuario creado: id={user.id} username={user.username} rol={role_name}")
        return 0
    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(main())
