"""Rutas internas sin RBAC global (token dedicado). Montar en main.py sin Depends(require_rbac)."""

from __future__ import annotations

from datetime import date
from secrets import compare_digest

from fastapi import APIRouter, Depends, Header, HTTPException, Query, Request, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from app.api.deps import get_db
from app.core.config import settings
from app.crud import user as user_crud
from app.models.role import Role
from app.models.user import User

router = APIRouter()


def _require_direccion_cron_secret(
    x_sife_direccion_cron_secret: str | None = Header(default=None, alias="X-SIFE-Direccion-Cron-Secret"),
) -> None:
    expected = (settings.DIRECCION_COMMITTEE_SNAPSHOT_CRON_SECRET or "").strip()
    if not expected:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Cron no habilitado: defina DIRECCION_COMMITTEE_SNAPSHOT_CRON_SECRET en el servidor.",
        )
    got = (x_sife_direccion_cron_secret or "").strip()
    if len(got) != len(expected) or not compare_digest(got, expected):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Cabecera X-SIFE-Direccion-Cron-Secret inválida o faltante.",
        )


def _actor_user_for_direccion_cron(db: Session) -> User:
    cfg = (settings.DIRECCION_COMMITTEE_SNAPSHOT_CRON_ACTOR_USERNAME or "").strip()
    if cfg:
        u = user_crud.get_by_username(db, cfg)
        if u is None or not u.is_active:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Usuario cron inexistente o inactivo.",
            )
        r = (u.role.name if u.role else "").strip().lower()
        if r not in {"admin", "direccion"}:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Usuario cron debe tener rol admin o direccion.",
            )
        return u
    stmt = (
        select(User)
        .join(Role, User.role_id == Role.id)
        .options(joinedload(User.role))
        .where(User.is_active.is_(True), func.lower(Role.name) == "admin")
        .order_by(User.id.asc())
        .limit(1)
    )
    u = db.execute(stmt).scalar_one_or_none()
    if u is not None:
        return u
    stmt = (
        select(User)
        .join(Role, User.role_id == Role.id)
        .options(joinedload(User.role))
        .where(User.is_active.is_(True), func.lower(Role.name) == "direccion")
        .order_by(User.id.asc())
        .limit(1)
    )
    u = db.execute(stmt).scalar_one_or_none()
    if u is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="No hay usuario activo con rol admin o direccion para ejecutar el snapshot.",
        )
    return u


@router.post(
    "/direccion/committee-snapshot",
    summary="Cron: congelar snapshot semanal del reporte integral (token dedicado, sin JWT)",
)
def cron_committee_snapshot(
    request: Request,
    db: Session = Depends(get_db),
    _: None = Depends(_require_direccion_cron_secret),
    week_start: date | None = Query(
        default=None,
        description="Cualquier fecha dentro de la semana ISO a congelar; por defecto la semana de hoy",
    ),
) -> dict:
    from app.api.routes.direccion import upsert_committee_snapshot_for_week

    actor = _actor_user_for_direccion_cron(db)
    return upsert_committee_snapshot_for_week(
        db,
        actor,
        request,
        week_start or date.today(),
        audit_action="cron_create",
    )
