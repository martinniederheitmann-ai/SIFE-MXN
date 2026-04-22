from __future__ import annotations

from fastapi.testclient import TestClient


def test_health(client: TestClient) -> None:
    r = client.get("/health")
    assert r.status_code == 200
    data = r.json()
    assert data.get("status") == "ok"
    assert "mysql_db" in data


def test_panel_css_static(client: TestClient) -> None:
    r = client.get("/static/panel/panel.css")
    assert r.status_code == 200
    body = r.text
    assert ".app-shell" in body or "app-shell" in body


def test_panel_js_static(client: TestClient) -> None:
    r = client.get("/static/panel/panel.js")
    assert r.status_code == 200
    body = r.text
    assert "const panelBoot" in body and "panelBoot.apiBase" in body
    assert "async function boot" in body or "function boot" in body
