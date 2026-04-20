from __future__ import annotations

import json
from typing import Any

from fastapi import Request
from sqlalchemy.inspection import inspect as sqlalchemy_inspect
from sqlalchemy.orm import Session

from app.api.deps import AuthContext
from app.models.audit_log import AuditLog


def model_to_dict(obj: Any) -> dict[str, Any]:
    if obj is None:
        return {}
    mapper = sqlalchemy_inspect(obj.__class__)
    out: dict[str, Any] = {}
    for column in mapper.columns:
        out[column.key] = getattr(obj, column.key, None)
    return out


def _is_sensitive_audit_key(key: str) -> bool:
    lower = key.lower()
    if lower in {"hashed_password", "password", "current_password", "new_password"}:
        return True
    if "password" in lower or "secret" in lower or lower.endswith("_token"):
        return True
    if lower == "api_key" or lower.endswith("_api_key"):
        return True
    return False


def _redact_audit_mapping(data: dict[str, Any] | None) -> dict[str, Any] | None:
    if data is None:
        return None
    out: dict[str, Any] = {}
    for k, v in data.items():
        if _is_sensitive_audit_key(k):
            out[k] = None if v is None else "***"
        else:
            out[k] = v
    return out


def _safe_json(value: Any) -> str | None:
    if value is None:
        return None
    return json.dumps(value, ensure_ascii=True, default=str)


def write_audit_log(
    db: Session,
    request: Request | None,
    *,
    entity: str,
    entity_id: str | int | None,
    action: str,
    before: dict[str, Any] | None = None,
    after: dict[str, Any] | None = None,
    meta: dict[str, Any] | None = None,
) -> None:
    auth: AuthContext | None = None
    if request is not None:
        auth = getattr(request.state, "auth_context", None)
    actor_type = "system"
    actor_username = None
    actor_role = None
    is_api_key = False
    if auth is not None:
        is_api_key = bool(auth.is_api_key)
        actor_type = "api_key" if is_api_key else "jwt"
        if auth.user is not None:
            actor_username = auth.user.username
            actor_role = auth.user.role.name if auth.user and auth.user.role else None

    rb = _redact_audit_mapping(before)
    ra = _redact_audit_mapping(after)
    rm = _redact_audit_mapping(meta)
    row = AuditLog(
        entity=entity,
        entity_id=str(entity_id) if entity_id is not None else None,
        action=action,
        actor_type=actor_type,
        actor_username=actor_username,
        actor_role=actor_role,
        is_api_key=is_api_key,
        source_path=str(request.url.path) if request is not None else None,
        source_method=request.method.upper() if request is not None else None,
        before_json=_safe_json(rb),
        after_json=_safe_json(ra),
        meta_json=_safe_json(rm),
    )
    db.add(row)
    db.commit()
