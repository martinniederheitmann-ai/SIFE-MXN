#!/usr/bin/env python3
"""Volcado lógico de MySQL usando credenciales de la app (.env / Settings).

Escribe un archivo .sql bajo backups/ con marca de tiempo. Requiere `mysqldump` en PATH.
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from app.core.config import settings  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Respaldo mysqldump de la base SIFE-MXN.")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=_REPO_ROOT / "backups",
        help="Directorio de salida (por defecto ./backups)",
    )
    parser.add_argument("--mysqldump", type=str, default="mysqldump", help="Ejecutable mysqldump")
    args = parser.parse_args()
    out_dir: Path = args.output_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_file = out_dir / f"sife_mxn_{settings.MYSQL_DB}_{ts}.sql"
    env = os.environ.copy()
    env["MYSQL_PWD"] = settings.MYSQL_PASSWORD
    cmd = [
        args.mysqldump,
        f"--host={settings.MYSQL_HOST}",
        f"--port={settings.MYSQL_PORT}",
        f"--user={settings.MYSQL_USER}",
        "--single-transaction",
        "--routines",
        "--events",
        settings.MYSQL_DB,
    ]
    try:
        with out_file.open("wb") as fh:
            subprocess.run(cmd, check=True, env=env, stdout=fh, stderr=subprocess.PIPE)
    except FileNotFoundError:
        print("No se encontró mysqldump. Instale el cliente MySQL o indique --mysqldump.", file=sys.stderr)
        return 2
    except subprocess.CalledProcessError as e:
        err = (e.stderr or b"").decode("utf-8", errors="replace")
        print(err or str(e), file=sys.stderr)
        if out_file.exists():
            out_file.unlink(missing_ok=True)
        return 1
    print(str(out_file.resolve()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
