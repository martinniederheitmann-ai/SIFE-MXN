from __future__ import annotations

from collections.abc import Generator
from dataclasses import dataclass
from secrets import compare_digest

import jwt
from fastapi import Depends, HTTPException, Security, status
from fastapi.security import APIKeyHeader, HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db as _get_db
from app.core.security import decode_access_token
from app.crud import user as user_crud
from app.models.user import User
from app.schemas.auth import UserPublic

api_key_header = APIKeyHeader(name=settings.API_KEY_HEADER, auto_error=False)
bearer_scheme = HTTPBearer(auto_error=False)


def get_db() -> Generator[Session, None, None]:
    yield from _get_db()


@dataclass
class AuthContext:
    """Contexto tras autenticación: API key (sin usuario) o JWT (con usuario)."""

    user: User | None
    is_api_key: bool


def _api_key_valid(api_key: str | None) -> bool:
    expected = settings.API_KEY.strip()
    if not expected:
        return False
    return api_key is not None and compare_digest(api_key.strip(), expected)


def require_auth(
    api_key: str | None = Security(api_key_header),
    bearer: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> AuthContext:
    """Acepta X-API-Key (como hasta ahora) o Authorization: Bearer <JWT>."""
    if _api_key_valid(api_key):
        return AuthContext(user=None, is_api_key=True)

    if bearer and bearer.credentials:
        if not settings.JWT_SECRET_KEY.strip():
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="JWT no configurado en el servidor.",
            )
        try:
            payload = decode_access_token(bearer.credentials)
        except jwt.PyJWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token invalido o expirado.",
            ) from None
        username = payload.get("sub")
        if not username or not isinstance(username, str):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token sin sujeto valido.",
            )
        user = user_crud.get_by_username(db, username)
        if user is None or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuario no encontrado o inactivo.",
            )
        return AuthContext(user=user, is_api_key=False)

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="API key o Bearer JWT requerido.",
    )


def require_api_key(api_key: str | None = Security(api_key_header)) -> None:
    """Compatibilidad: solo API key (p. ej. health interno si se usara)."""
    expected_api_key = settings.API_KEY.strip()
    if not expected_api_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="La API no tiene una API key configurada.",
        )

    if api_key is None or not compare_digest(api_key, expected_api_key):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key invalida o faltante.",
        )


def get_current_user_jwt(
    bearer: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    """Solo JWT (para /auth/me). La API key no identifica usuario."""
    if not bearer or not bearer.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Se requiere Authorization: Bearer.",
        )
    if not settings.JWT_SECRET_KEY.strip():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="JWT no configurado en el servidor.",
        )
    try:
        payload = decode_access_token(bearer.credentials)
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalido o expirado.",
        ) from None
    username = payload.get("sub")
    if not username or not isinstance(username, str):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token sin sujeto valido.",
        )
    user = user_crud.get_by_username(db, username)
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado o inactivo.",
        )
    return user


def user_to_public(user: User) -> UserPublic:
    return UserPublic(
        id=user.id,
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        is_active=user.is_active,
        role_name=user.role.name if user.role else "",
    )
