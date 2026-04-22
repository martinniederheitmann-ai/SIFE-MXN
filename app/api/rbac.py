"""
Control de acceso por rol para rutas bajo API_V1_PREFIX (JWT/API key).

- API key (X-API-Key): restringida por prefijos de settings (hardening).
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
        "bajas-danos",
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
            "bajas-danos",
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
            "bajas-danos",
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


def _csv_to_set(raw: str | None) -> set[str]:
    if not raw:
        return set()
    return {x.strip().lower() for x in raw.split(",") if x.strip()}


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
    request.state.auth_context = auth
    request.state.is_api_key_auth = bool(auth.is_api_key)
    request.state.actor_username = auth.user.username if auth.user is not None else None

    method = request.method.upper()
    segment = _first_path_segment(request.url.path)

    if auth.is_api_key:
        deny_all = _csv_to_set(settings.API_KEY_DENY_PREFIXES)
        deny_write = _csv_to_set(settings.API_KEY_WRITE_DENY_PREFIXES)
        if segment and segment in deny_all:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"API key no autorizada para el recurso '/{segment}'.",
            )
        if method not in READONLY_METHODS and segment and segment in deny_write:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"API key en modo hardening: escritura bloqueada para '/{segment}'.",
            )
        return auth
    user = auth.user
    if user is None or user.role is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario sin rol asignado.",
        )
    role = (user.role.name or "").strip().lower()
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
