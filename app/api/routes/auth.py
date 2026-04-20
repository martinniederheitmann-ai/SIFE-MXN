from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.api.deps import get_current_user_jwt, get_db, user_to_public
from app.models.user import User
from app.core.config import settings
from app.core.security import create_access_token, hash_password, verify_password
from app.crud import user as user_crud
from app.schemas.auth import PasswordChangeBody, TokenResponse, UserPublic
from app.services.audit import write_audit_log

router = APIRouter()


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Obtener token JWT (usuario y contraseña)",
)
def login(
    request: Request,
    form: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
) -> TokenResponse:
    if not settings.JWT_SECRET_KEY.strip():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="JWT_SECRET_KEY no configurada en el servidor.",
        )
    user = user_crud.get_by_username(db, form.username.strip())
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos.",
        )
    if not verify_password(form.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos.",
        )
    role_name = user.role.name if user.role else "sin_rol"
    token = create_access_token(subject=user.username, role_name=role_name)
    write_audit_log(
        db,
        request,
        entity="auth",
        entity_id=user.id,
        action="login",
        meta={"username": user.username},
    )
    return TokenResponse(
        access_token=token,
        expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.get(
    "/me",
    response_model=UserPublic,
    summary="Usuario autenticado (solo Bearer JWT)",
)
def me(user: User = Depends(get_current_user_jwt)) -> UserPublic:
    return user_to_public(user)


@router.post(
    "/change-password",
    summary="Cambiar la propia contraseña (JWT)",
)
def change_password(
    body: PasswordChangeBody,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user_jwt),
) -> dict:
    if not verify_password(body.current_password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Contraseña actual incorrecta.",
        )
    user.hashed_password = hash_password(body.new_password)
    db.add(user)
    db.commit()
    write_audit_log(
        db,
        request,
        entity="auth",
        entity_id=user.id,
        action="change_password",
        meta={"username": user.username},
    )
    return {"ok": True}
