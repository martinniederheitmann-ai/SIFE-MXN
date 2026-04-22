from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import func, select

from app.core.config import settings
from app.core.database import SessionLocal
from app.core.security import create_access_token
from app.models.role import Role
from app.models.user import User


def _username_for_role(role_name: str) -> str | None:
    rlow = role_name.strip().lower()
    with SessionLocal() as db:
        row = db.execute(
            select(User.username)
            .join(Role, User.role_id == Role.id)
            .where(User.is_active.is_(True), func.lower(Role.name) == rlow)
            .order_by(User.id.asc())
            .limit(1)
        ).first()
        return str(row[0]) if row else None


def _username_for_any_role(role_names: list[str]) -> tuple[str | None, str | None]:
    for role_name in role_names:
        uname = _username_for_role(role_name)
        if uname:
            return uname, role_name
    return None, None


def test_api_key_allows_get_bajas_danos(client: TestClient) -> None:
    key = (settings.API_KEY or "").strip()
    if not key:
        return
    r = client.get("/api/v1/bajas-danos?limit=1", headers={settings.API_KEY_HEADER: key})
    assert r.status_code == 200
    body = r.json()
    assert body.get("items") is not None
    assert "total" in body


@pytest.mark.skipif(not (settings.JWT_SECRET_KEY or "").strip(), reason="JWT_SECRET_KEY no configurada")
def test_jwt_operaciones_can_get_bajas_danos(client: TestClient) -> None:
    uname = _username_for_role("operaciones")
    if not uname:
        pytest.skip("No hay usuario activo con rol operaciones en la base de pruebas.")
    token = create_access_token(subject=uname, role_name="operaciones")
    r = client.get(
        "/api/v1/bajas-danos?limit=1",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 200


@pytest.mark.skipif(not (settings.JWT_SECRET_KEY or "").strip(), reason="JWT_SECRET_KEY no configurada")
def test_jwt_ventas_forbidden_bajas_danos(client: TestClient) -> None:
    uname = _username_for_role("ventas")
    if not uname:
        pytest.skip("No hay usuario activo con rol ventas en la base de pruebas.")
    token = create_access_token(subject=uname, role_name="ventas")
    r = client.get(
        "/api/v1/bajas-danos?limit=1",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 403


@pytest.mark.skipif(not (settings.JWT_SECRET_KEY or "").strip(), reason="JWT_SECRET_KEY no configurada")
def test_jwt_direccion_or_admin_can_get_decision_guardrails(client: TestClient) -> None:
    uname, role_name = _username_for_any_role(["direccion", "admin"])
    if not uname or not role_name:
        pytest.skip("No hay usuario activo con rol direccion/admin en la base de pruebas.")
    token = create_access_token(subject=uname, role_name=role_name)
    r = client.get(
        "/api/v1/direccion/reportes/decision-guardrails",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 200
    payload = r.json()
    assert "bloqueado" in payload
    assert "items" in payload


@pytest.mark.skipif(not (settings.JWT_SECRET_KEY or "").strip(), reason="JWT_SECRET_KEY no configurada")
def test_jwt_direccion_or_admin_can_create_action_from_guardrail(client: TestClient) -> None:
    uname, role_name = _username_for_any_role(["direccion", "admin"])
    if not uname or not role_name:
        pytest.skip("No hay usuario activo con rol direccion/admin en la base de pruebas.")
    token = create_access_token(subject=uname, role_name=role_name)
    r = client.post(
        "/api/v1/direccion/acciones/from-guardrail",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "regla": "margen_minimo",
            "motivo": "Prueba automatizada de guardrail.",
            "owner": "finanzas",
            "dias_compromiso": 7,
        },
    )
    assert r.status_code == 200
    payload = r.json()
    assert str(payload.get("titulo", "")).startswith("[GUARDRAIL]")


@pytest.mark.skipif(not (settings.JWT_SECRET_KEY or "").strip(), reason="JWT_SECRET_KEY no configurada")
def test_jwt_direccion_or_admin_can_get_acciones_impacto(client: TestClient) -> None:
    uname, role_name = _username_for_any_role(["direccion", "admin"])
    if not uname or not role_name:
        pytest.skip("No hay usuario activo con rol direccion/admin en la base de pruebas.")
    token = create_access_token(subject=uname, role_name=role_name)
    r = client.get(
        "/api/v1/direccion/acciones/impacto",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 200
    payload = r.json()
    assert "items" in payload
    assert "impacto_total_estimado_mxn" in payload
    assert "impacto_total_realizado_mxn" in payload


@pytest.mark.skipif(not (settings.JWT_SECRET_KEY or "").strip(), reason="JWT_SECRET_KEY no configurada")
def test_jwt_direccion_or_admin_can_get_acciones_roi(client: TestClient) -> None:
    uname, role_name = _username_for_any_role(["direccion", "admin"])
    if not uname or not role_name:
        pytest.skip("No hay usuario activo con rol direccion/admin en la base de pruebas.")
    token = create_access_token(subject=uname, role_name=role_name)
    r = client.get(
        "/api/v1/direccion/acciones/impacto/roi?limit=5",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 200
    payload = r.json()
    assert "items" in payload


@pytest.mark.skipif(not (settings.JWT_SECRET_KEY or "").strip(), reason="JWT_SECRET_KEY no configurada")
def test_jwt_direccion_or_admin_can_get_destruye_margen(client: TestClient) -> None:
    uname, role_name = _username_for_any_role(["direccion", "admin"])
    if not uname or not role_name:
        pytest.skip("No hay usuario activo con rol direccion/admin en la base de pruebas.")
    token = create_access_token(subject=uname, role_name=role_name)
    r = client.get(
        "/api/v1/direccion/reportes/destruye-margen?limit=5",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 200
    payload = r.json()
    assert "clientes" in payload
    assert "rutas" in payload


@pytest.mark.skipif(not (settings.JWT_SECRET_KEY or "").strip(), reason="JWT_SECRET_KEY no configurada")
def test_jwt_direccion_or_admin_can_get_estado_guerra(client: TestClient) -> None:
    uname, role_name = _username_for_any_role(["direccion", "admin"])
    if not uname or not role_name:
        pytest.skip("No hay usuario activo con rol direccion/admin en la base de pruebas.")
    token = create_access_token(subject=uname, role_name=role_name)
    r = client.get(
        "/api/v1/direccion/reportes/estado-guerra",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 200
    payload = r.json()
    assert "semaforo_general" in payload
    assert "top_prioridades" in payload


@pytest.mark.skipif(not (settings.JWT_SECRET_KEY or "").strip(), reason="JWT_SECRET_KEY no configurada")
def test_jwt_direccion_or_admin_can_create_action_from_recommendation(client: TestClient) -> None:
    uname, role_name = _username_for_any_role(["direccion", "admin"])
    if not uname or not role_name:
        pytest.skip("No hay usuario activo con rol direccion/admin en la base de pruebas.")
    token = create_access_token(subject=uname, role_name=role_name)
    r = client.post(
        "/api/v1/direccion/acciones/from-recommendation",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "source_type": "cliente",
            "source_name": "Cliente Prueba DM",
            "accion_sugerida": "Renegociar tarifa y plazo de cobro.",
            "owner": "comercial",
            "dias_compromiso": 7,
        },
    )
    assert r.status_code == 200
    payload = r.json()
    assert str(payload.get("titulo", "")).startswith("[DESTRUYE-MARGEN:cliente]")


@pytest.mark.skipif(not (settings.JWT_SECRET_KEY or "").strip(), reason="JWT_SECRET_KEY no configurada")
def test_jwt_direccion_or_admin_can_close_action_with_impact(client: TestClient) -> None:
    uname, role_name = _username_for_any_role(["direccion", "admin"])
    if not uname or not role_name:
        pytest.skip("No hay usuario activo con rol direccion/admin en la base de pruebas.")
    token = create_access_token(subject=uname, role_name=role_name)
    created = client.post(
        "/api/v1/direccion/acciones/from-guardrail",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "regla": "viajes_vacios_maximos",
            "motivo": "Prueba cierre de impacto.",
            "owner": "operaciones",
            "dias_compromiso": 7,
        },
    )
    assert created.status_code == 200
    accion_id = int(created.json().get("id"))
    closed = client.post(
        f"/api/v1/direccion/acciones/{accion_id}/cerrar-impacto",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "impacto_realizado_mxn": 1500,
            "comentario_cierre": "Se consiguió retorno de prueba y ajuste operativo.",
            "marcar_completada": True,
        },
    )
    assert closed.status_code == 200
    payload = closed.json()
    assert payload.get("estatus") == "completada"
