"""Consulta de pista de auditoría (solo JWT admin o dirección)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import AuthContext, get_db
from app.models.audit_log import AuditLog
from app.schemas.audit_log import AuditLogItem, AuditLogListResponse

router = APIRouter()


def _require_jwt_admin_direccion(request: Request) -> None:
    """Ejecutar tras require_rbac: solo JWT con rol admin o dirección."""
    auth: AuthContext | None = getattr(request.state, "auth_context", None)
    if auth is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No autenticado.",
        )
    if auth.is_api_key:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="La auditoría no está disponible con API key.",
        )
    if auth.user is None or auth.user.role is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario sin rol.",
        )
    role = (auth.user.role.name or "").strip().lower()
    if role not in {"admin", "direccion"}:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo admin o dirección pueden consultar la auditoría.",
        )


@router.get(
    "",
    response_model=AuditLogListResponse,
    summary="Listar registros de auditoría",
)
def listar_audit_logs(
    db: Session = Depends(get_db),
    _: None = Depends(_require_jwt_admin_direccion),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    entity: str | None = Query(None, max_length=80),
    entity_id: str | None = Query(None, max_length=80),
    action: str | None = Query(None, max_length=32),
    actor_username: str | None = Query(None, max_length=120),
) -> AuditLogListResponse:
    conds: list = []
    if entity:
        conds.append(AuditLog.entity == entity)
    if entity_id:
        conds.append(AuditLog.entity_id == entity_id)
    if action:
        conds.append(AuditLog.action == action)
    if actor_username:
        conds.append(AuditLog.actor_username == actor_username)

    base = select(AuditLog)
    count_stmt = select(func.count()).select_from(AuditLog)
    if conds:
        base = base.where(*conds)
        count_stmt = count_stmt.where(*conds)

    total = int(db.execute(count_stmt).scalar_one() or 0)
    stmt = base.order_by(AuditLog.created_at.desc()).offset(skip).limit(limit)
    rows = list(db.execute(stmt).scalars().all())
    return AuditLogListResponse(
        items=[AuditLogItem.model_validate(r) for r in rows],
        total=total,
        skip=skip,
        limit=limit,
    )
