from __future__ import annotations

from fastapi.testclient import TestClient

from app.core.config import settings


def test_api_v1_requires_credentials(client: TestClient) -> None:
    r = client.get("/api/v1/viajes?limit=1")
    assert r.status_code == 401


def test_api_key_allows_read_viajes(client: TestClient) -> None:
    key = (settings.API_KEY or "").strip()
    if not key:
        return
    r = client.get("/api/v1/viajes?limit=1", headers={settings.API_KEY_HEADER: key})
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, dict)
    assert "items" in data and "total" in data


def test_api_key_denied_direccion(client: TestClient) -> None:
    key = (settings.API_KEY or "").strip()
    if not key:
        return
    r = client.get(
        "/api/v1/direccion/dashboard",
        headers={settings.API_KEY_HEADER: key},
    )
    assert r.status_code == 403
    assert "direccion" in (r.json().get("detail") or "").lower()


def test_api_key_denied_usuarios_roles(client: TestClient) -> None:
    key = (settings.API_KEY or "").strip()
    if not key:
        return
    r = client.get(
        "/api/v1/usuarios/roles",
        headers={settings.API_KEY_HEADER: key},
    )
    assert r.status_code == 403
