"""Alta y mantenimiento de usuarios (JWT admin/direccion; API key sin restriccion de rol)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import AuthContext, get_db
from app.api.rbac import require_rbac
from app.core.security import hash_password
from app.crud import user as user_crud
from app.models.user import User
from app.schemas.usuario_admin import (
    RolePublic,
    UsuarioActualizar,
    UsuarioCrear,
    UsuarioListaItem,
    UsuarioPasswordAdmin,
)

router = APIRouter()


def _actor_lower(auth: AuthContext) -> str:
    if auth.is_api_key or not auth.user or not auth.user.role:
        return "admin"
    return (auth.user.role.name or "").strip().lower()


def require_user_manager(auth: AuthContext = Depends(require_rbac)) -> AuthContext:
    if auth.is_api_key:
        return auth
    r = _actor_lower(auth)
    if r not in ("admin", "direccion"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Gestion de usuarios: requiere rol admin o direccion.",
        )
    return auth


def _deny_direccion_on_admin(*, actor: str, target: User | None, new_role: str | None) -> None:
    if actor == "admin":
        return
    if actor != "direccion":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Sin permiso.")
    if new_role and new_role.strip().lower() == "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo el rol admin puede asignar o crear usuarios con rol admin.",
        )
    if target and target.role and target.role.name.strip().lower() == "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo admin puede modificar cuentas con rol admin.",
        )


def _filter_list_for_actor(actor: str, users: list[User]) -> list[User]:
    if actor == "direccion":
        return [u for u in users if not u.role or u.role.name.strip().lower() != "admin"]
    return users


@router.get("/roles", response_model=list[RolePublic], summary="Catalogo de roles")
def list_roles_ep(
    db: Session = Depends(get_db),
    _auth: AuthContext = Depends(require_user_manager),
):
    roles = user_crud.list_roles(db)
    return [RolePublic(name=r.name, description=r.description) for r in roles]


@router.get("/", response_model=list[UsuarioListaItem], summary="Listar usuarios")
def list_usuarios(
    db: Session = Depends(get_db),
    auth: AuthContext = Depends(require_user_manager),
):
    actor = _actor_lower(auth)
    users = user_crud.list_users_ordered(db)
    users = _filter_list_for_actor(actor, users)
    return [
        UsuarioListaItem(
            id=u.id,
            username=u.username,
            role_name=u.role.name if u.role else "",
            is_active=u.is_active,
            email=u.email,
            full_name=u.full_name,
        )
        for u in users
    ]


@router.post(
    "/",
    response_model=UsuarioListaItem,
    status_code=status.HTTP_201_CREATED,
    summary="Crear usuario",
)
def crear_usuario(
    body: UsuarioCrear,
    db: Session = Depends(get_db),
    auth: AuthContext = Depends(require_user_manager),
):
    actor = _actor_lower(auth)
    uname = body.username.strip()
    if user_crud.get_by_username(db, uname):
        raise HTTPException(status_code=400, detail="Ya existe ese nombre de usuario.")
    role_name = body.role_name.strip()
    _deny_direccion_on_admin(actor=actor, target=None, new_role=role_name)
    role = user_crud.get_role_by_name(db, role_name)
    if role is None:
        raise HTTPException(status_code=400, detail=f"Rol desconocido: {role_name}")
    u = user_crud.create_user(
        db,
        username=uname,
        hashed_password=hash_password(body.password),
        role_id=role.id,
        email=body.email.strip() if body.email and body.email.strip() else None,
        full_name=body.full_name.strip() if body.full_name and body.full_name.strip() else None,
    )
    u = user_crud.get_by_id(db, u.id)
    assert u is not None
    return UsuarioListaItem(
        id=u.id,
        username=u.username,
        role_name=u.role.name if u.role else "",
        is_active=u.is_active,
        email=u.email,
        full_name=u.full_name,
    )


@router.patch("/{user_id}", response_model=UsuarioListaItem, summary="Actualizar usuario")
def actualizar_usuario(
    user_id: int,
    body: UsuarioActualizar,
    db: Session = Depends(get_db),
    auth: AuthContext = Depends(require_user_manager),
):
    actor = _actor_lower(auth)
    u = user_crud.get_by_id(db, user_id)
    if u is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")
    new_role_name = body.role_name.strip() if body.role_name else None
    _deny_direccion_on_admin(actor=actor, target=u, new_role=new_role_name)
    if body.email is not None:
        u.email = body.email.strip() or None
    if body.full_name is not None:
        u.full_name = body.full_name.strip() or None
    if body.is_active is not None:
        u.is_active = body.is_active
    if new_role_name:
        role = user_crud.get_role_by_name(db, new_role_name)
        if role is None:
            raise HTTPException(status_code=400, detail=f"Rol desconocido: {new_role_name}")
        u.role_id = role.id
    db.add(u)
    db.commit()
    db.refresh(u)
    u = user_crud.get_by_id(db, user_id)
    assert u is not None
    return UsuarioListaItem(
        id=u.id,
        username=u.username,
        role_name=u.role.name if u.role else "",
        is_active=u.is_active,
        email=u.email,
        full_name=u.full_name,
    )


@router.post("/{user_id}/password", summary="Establecer contraseña (admin/direccion)")
def set_password_admin(
    user_id: int,
    body: UsuarioPasswordAdmin,
    db: Session = Depends(get_db),
    auth: AuthContext = Depends(require_user_manager),
):
    actor = _actor_lower(auth)
    u = user_crud.get_by_id(db, user_id)
    if u is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")
    _deny_direccion_on_admin(actor=actor, target=u, new_role=None)
    u.hashed_password = hash_password(body.new_password)
    db.add(u)
    db.commit()
    return {"ok": True}
