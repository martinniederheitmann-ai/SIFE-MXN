from collections.abc import Generator
from secrets import compare_digest

from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db as _get_db

api_key_header = APIKeyHeader(name=settings.API_KEY_HEADER, auto_error=False)


def get_db() -> Generator[Session, None, None]:
    yield from _get_db()


def require_api_key(api_key: str | None = Security(api_key_header)) -> None:
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
