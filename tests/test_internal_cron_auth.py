from __future__ import annotations

from fastapi.testclient import TestClient

from app.core.config import settings


def test_committee_snapshot_without_cron_header_is_rejected(client: TestClient) -> None:
    r = client.post("/api/v1/internal/direccion/committee-snapshot")
    # Sin cabecera: 401 si el cron está configurado; 503 si el secreto ni siquiera está definido.
    assert r.status_code in (401, 503)


def test_committee_snapshot_wrong_secret_returns_401(client: TestClient) -> None:
    expected = (settings.DIRECCION_COMMITTEE_SNAPSHOT_CRON_SECRET or "").strip()
    if not expected:
        r = client.post(
            "/api/v1/internal/direccion/committee-snapshot",
            headers={"X-SIFE-Direccion-Cron-Secret": "wrong"},
        )
        assert r.status_code == 503
        return
    r = client.post(
        "/api/v1/internal/direccion/committee-snapshot",
        headers={"X-SIFE-Direccion-Cron-Secret": "definitely-not-the-secret"},
    )
    assert r.status_code == 401
