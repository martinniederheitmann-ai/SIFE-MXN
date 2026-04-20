"""
Control de acceso por rol para rutas bajo API_V1_PREFIX (JWT).

- API key (X-API-Key): sin cambios; acceso total (integraciones / panel sin usuario).
- JWT: el primer segmento de ruta tras el prefijo debe estar permitido para el rol.
- consulta: solo GET/HEAD/OPTIONS en recursos conocidos.
- admin: todo.
"""

from __future__ import annotations

from fastapi import Depends, HTTPException, Request, status

from app.api.deps import AuthContext, require_auth
from app.core.config import settings

# Debe coincidir con los `prefix=` de app/api/routes/__init__.py (sin slash inicial).
ALL_API_PREFIXES: frozenset[str] = frozenset(
    {
        "viajes",
        "clientes",
        "facturas",
        "transportistas",
        "fletes",
        "motor-tarifas",
        "gastos-viaje",
        "tarifas-compra-transportista",
        "tarifas-flete",
        "ordenes-servicio",
        "operadores",
        "unidades",
        "asignaciones",
        "despachos",
        "direccion",
        "cumplimiento",
        "usuarios",
    }
)

# Alineado con el menú del panel (ROLE_PAGE_SET en app/web.py).
ROLE_PREFIXES: dict[str, frozenset[str]] = {
    "operaciones": frozenset(
        {
            "viajes",
            "transportistas",
            "fletes",
            "operadores",
            "unidades",
            "asignaciones",
            "gastos-viaje",
            "despachos",
            "cumplimiento",
            "motor-tarifas",
            "ordenes-servicio",
        }
    ),
    "contabilidad": frozenset(
        {
            "clientes",
            "transportistas",
            "viajes",
            "fletes",
            "facturas",
            "gastos-viaje",
            "tarifas-flete",
            "tarifas-compra-transportista",
            "motor-tarifas",
            "ordenes-servicio",
            "cumplimiento",
        }
    ),
    "ventas": frozenset(
        {
            "clientes",
            "transportistas",
            "viajes",
            "fletes",
            "tarifas-flete",
            "tarifas-compra-transportista",
            "facturas",
            "motor-tarifas",
            "ordenes-servicio",
            "cumplimiento",
        }
    ),
}

READONLY_METHODS: frozenset[str] = frozenset({"GET", "HEAD", "OPTIONS"})


def _first_path_segment(path: str) -> str:
    base = settings.API_V1_PREFIX.rstrip("/")
    p = path.rstrip("/")
    if not p.startswith(base):
        return ""
    rest = p[len(base) :].lstrip("/")
    if not rest:
        return ""
    return rest.split("/", 1)[0]


def require_rbac(request: Request, auth: AuthContext = Depends(require_auth)) -> AuthContext:
    if auth.is_api_key:
        return auth
    user = auth.user
    if user is None or user.role is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario sin rol asignado.",
        )
    role = (user.role.name or "").strip().lower()
    method = request.method.upper()
    segment = _first_path_segment(request.url.path)

    if role in ("admin", "direccion"):
        return auth

    if role == "consulta":
        if segment == "usuarios":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Rol consulta no puede acceder a gestion de usuarios.",
            )
        if method not in READONLY_METHODS:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Rol consulta: solo lectura (GET, HEAD, OPTIONS).",
            )
        if not segment or segment in ALL_API_PREFIXES:
            return auth
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Rol consulta: recurso no permitido.",
        )

    allowed = ROLE_PREFIXES.get(role)
    if allowed is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Rol '{role}' sin permisos de API configurados.",
        )
    if not segment or segment not in allowed:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Rol '{role}' no autorizado para el recurso '/{segment}'.",
        )
    return auth
