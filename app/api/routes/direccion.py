from __future__ import annotations

import csv
import io
import json
from datetime import UTC, date, datetime, time, timedelta
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user_jwt, get_db
from app.core.config import settings
from app.models.asignacion import Asignacion
from app.models.despacho import Despacho, DespachoEvento, EstadoDespacho, TipoEventoDespacho
from app.models.direccion import (
    AccionEstatus,
    DireccionAccion,
    DireccionIncidencia,
    IncidenciaEstatus,
    IncidenciaSeveridad,
)
from app.models.direccion_kpi_config import DireccionKpiConfig, DireccionKpiConfigHistory
from app.models.direccion_semanal_reporte_snapshot import DireccionSemanalReporteSnapshot
from app.models.cotizacion_flete import CotizacionFlete, EstatusCotizacionFlete
from app.models.cliente import Cliente
from app.models.factura import EstatusFactura, Factura
from app.models.flete import EstadoFlete, Flete
from app.models.orden_servicio import OrdenServicio
from app.models.role import Role
from app.models.user import User
from app.models.viaje import Viaje
from app.schemas.direccion import (
    DireccionBucketAntiguedad,
    DireccionAccionCreate,
    DireccionAccionRead,
    DireccionAccionFromGuardrailCreate,
    DireccionAccionFromRecommendationCreate,
    DireccionAccionCerrarImpactoCreate,
    DireccionAccionSeguimientoRead,
    DireccionAccionImpactoItem,
    DireccionAccionImpactoRead,
    DireccionAccionRoiItem,
    DireccionAccionRoiRead,
    DireccionDestruyeMargenClienteItem,
    DireccionDestruyeMargenRutaItem,
    DireccionDestruyeMargenRead,
    DireccionEstadoGuerraRead,
    DireccionAccionUpdate,
    DireccionDashboardResponse,
    DireccionEmbudo,
    DireccionIncidenciaCreate,
    DireccionIncidenciaRead,
    DireccionIncidenciaUpdate,
    DireccionKpiResumen,
    DireccionReporteCartera,
    DireccionReporteClienteRentabilidad,
    DireccionReporteCompletoResponse,
    DireccionReporteConversion,
    DireccionReporteFinanciero,
    DireccionReporteProductividad,
    DireccionReporteSostenibilidad,
    DireccionDecisionGuardrailItem,
    DireccionDecisionGuardrailsRead,
    DireccionThresholdHistoryRead,
    DireccionThresholdPolicyRead,
    DireccionThresholdPolicyUpdate,
    DireccionSemanalSnapshotItem,
    DireccionSemanalSnapshotListResponse,
    DireccionThresholds,
    DireccionThresholdsRead,
    DireccionThresholdsUpdate,
    DireccionSemaforo,
    DireccionTiemposCiclo,
)
from app.services.audit import model_to_dict, write_audit_log

router = APIRouter()


def _require_direccion_or_admin(user: User) -> None:
    role = (user.role.name if user.role else "").strip().lower()
    if role not in {"admin", "direccion"}:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo admin o direccion pueden consultar el tablero de direccion.",
        )


def _require_admin(user: User) -> None:
    role = (user.role.name if user.role else "").strip().lower()
    if role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo admin puede gestionar umbrales por rol.",
        )


def _threshold_user_edit_allowed(user: User) -> tuple[bool, str | None]:
    """Ventana de edición de umbrales (override usuario). Admin siempre puede vía endpoints de rol."""
    if not settings.DIRECCION_THRESHOLD_EDIT_WINDOW_ENABLED:
        return True, None
    role = (user.role.name if user.role else "").strip().lower()
    if role == "admin":
        return True, None
    tz_name = (settings.DIRECCION_THRESHOLD_EDIT_TIMEZONE or "UTC").strip() or "UTC"
    try:
        tz = ZoneInfo(tz_name)
    except Exception:
        tz = ZoneInfo("UTC")
    now = datetime.now(tz)
    wd = now.weekday()
    ws = int(settings.DIRECCION_THRESHOLD_EDIT_WEEKDAY_START)
    we = int(settings.DIRECCION_THRESHOLD_EDIT_WEEKDAY_END)
    if ws <= we:
        if wd < ws or wd > we:
            return False, "Operación cerrada: fuera del calendario permitido para editar umbrales."
    elif not (wd >= ws or wd <= we):
        return False, "Operación cerrada: fuera del calendario permitido para editar umbrales."
    h = now.hour
    hs = int(settings.DIRECCION_THRESHOLD_EDIT_HOUR_START)
    he = int(settings.DIRECCION_THRESHOLD_EDIT_HOUR_END)
    if h < hs or h >= he:
        return False, "Operación cerrada: fuera del horario permitido para editar umbrales."
    return True, None


def _clamp_range(desde: date | None, hasta: date | None) -> tuple[date, date]:
    today = date.today()
    end = hasta or today
    start = desde or (end - timedelta(days=6))
    if start > end:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="'desde' no puede ser mayor que 'hasta'.",
        )
    return start, end


def _range_dt(start: date, end: date) -> tuple[datetime, datetime]:
    since_dt = datetime.combine(start, time.min)
    until_dt = datetime.combine(end + timedelta(days=1), time.min)
    return since_dt, until_dt


def _count_in_range(db: Session, model, field, since_dt: datetime, until_dt: datetime) -> int:
    stmt = select(func.count()).select_from(model).where(field >= since_dt, field < until_dt)
    return int(db.execute(stmt).scalar_one() or 0)


def _avg_hours_from_pairs(pairs: list[tuple[datetime | None, datetime | None]]) -> float | None:
    seconds: list[float] = []
    for start_dt, end_dt in pairs:
        if start_dt is None or end_dt is None:
            continue
        delta = (end_dt - start_dt).total_seconds()
        if delta >= 0:
            seconds.append(delta)
    if not seconds:
        return None
    return round((sum(seconds) / len(seconds)) / 3600, 2)


def _ratio(numerator: int, denominator: int) -> float:
    if denominator <= 0:
        return 0.0
    return round((numerator / denominator) * 100, 2)


def _ratio_amount(numerator: float, denominator: float) -> float:
    if denominator <= 0:
        return 0.0
    return round((numerator / denominator) * 100, 2)


def _safe_float(value) -> float:
    if value is None:
        return 0.0
    return float(value)


def _default_thresholds_dict() -> dict[str, float]:
    return {
        "margen_verde_min": 15.0,
        "margen_amarillo_min": 8.0,
        "utilidad_km_verde_min": 5.0,
        "utilidad_km_amarillo_min": 2.0,
        "conversion_verde_min": 30.0,
        "conversion_amarillo_min": 20.0,
        "vencida_verde_max": 20.0,
        "vencida_amarillo_max": 35.0,
        "carga_verde_min": 80.0,
        "carga_amarillo_min": 65.0,
    }


def _to_thresholds(payload: dict) -> DireccionThresholds:
    base = _default_thresholds_dict()
    merged = {**base, **(payload or {})}
    return DireccionThresholds(**merged)


def _thresholds_diff(before_cfg: dict, after_cfg: dict) -> list[str]:
    keys = sorted(set(before_cfg.keys()) | set(after_cfg.keys()))
    changes: list[str] = []
    for key in keys:
        before_v = float(before_cfg.get(key, 0))
        after_v = float(after_cfg.get(key, 0))
        if before_v != after_v:
            changes.append(f"{key}: {before_v} -> {after_v}")
    return changes


def _get_threshold_config_for_user(db: Session, user: User) -> tuple[str, DireccionKpiConfig | None]:
    user_scope = f"user:{user.id}"
    role_name = (user.role.name if user.role else "").strip().lower()
    role_scope = f"role:{role_name}" if role_name else ""
    user_override_allowed = True
    if role_name:
        policy_stmt = select(DireccionKpiConfig).where(
            DireccionKpiConfig.scope_type == "policy",
            DireccionKpiConfig.scope_value == f"role:{role_name}",
        )
        policy_row = db.execute(policy_stmt).scalar_one_or_none()
        if policy_row is not None:
            try:
                payload = json.loads(policy_row.config_json or "{}")
                user_override_allowed = bool(payload.get("user_override_allowed", True))
            except Exception:
                user_override_allowed = True
    stmt_user = select(DireccionKpiConfig).where(
        DireccionKpiConfig.scope_type == "user",
        DireccionKpiConfig.scope_value == user_scope,
    )
    user_cfg = db.execute(stmt_user).scalar_one_or_none()
    if user_cfg is not None and user_override_allowed:
        return "user", user_cfg
    if role_scope:
        stmt_role = select(DireccionKpiConfig).where(
            DireccionKpiConfig.scope_type == "role",
            DireccionKpiConfig.scope_value == role_scope,
        )
        role_cfg = db.execute(stmt_role).scalar_one_or_none()
        if role_cfg is not None:
            return ("role_locked" if not user_override_allowed else "role"), role_cfg
    return "default", None


def _get_role_override_policy(db: Session, role_name: str) -> bool:
    role_norm = (role_name or "").strip().lower()
    if not role_norm:
        return True
    stmt = select(DireccionKpiConfig).where(
        DireccionKpiConfig.scope_type == "policy",
        DireccionKpiConfig.scope_value == f"role:{role_norm}",
    )
    row = db.execute(stmt).scalar_one_or_none()
    if row is None:
        return True
    try:
        payload = json.loads(row.config_json or "{}")
        return bool(payload.get("user_override_allowed", True))
    except Exception:
        return True


def _sum_flete_field(db: Session, field, since_dt: datetime, until_dt: datetime) -> float:
    stmt = select(func.coalesce(func.sum(field), 0)).where(Flete.created_at >= since_dt, Flete.created_at < until_dt)
    return round(_safe_float(db.execute(stmt).scalar_one()), 2)


def _sum_factura_field(db: Session, field, since_dt: datetime, until_dt: datetime) -> float:
    stmt = select(func.coalesce(func.sum(field), 0)).where(Factura.created_at >= since_dt, Factura.created_at < until_dt)
    return round(_safe_float(db.execute(stmt).scalar_one()), 2)


def _build_decision_guardrails(
    db: Session, user: User, start_date: date, end_date: date
) -> DireccionDecisionGuardrailsRead:
    _require_direccion_or_admin(user)
    since_dt, until_dt = _range_dt(start_date, end_date)
    margen_min = 20.0
    dias_pago_max = 30
    vacio_max = 15.0

    ingresos_facturados = _sum_factura_field(db, Factura.total, since_dt, until_dt)
    costo_viaje_real = _sum_flete_field(
        db, func.coalesce(Flete.costo_transporte_real, Flete.costo_transporte_estimado, 0), since_dt, until_dt
    )
    utilidad_real = ingresos_facturados - costo_viaje_real
    margen_pct = _ratio_amount(utilidad_real, ingresos_facturados)

    fletes_totales_stmt = (
        select(func.count()).select_from(Flete).where(Flete.created_at >= since_dt, Flete.created_at < until_dt)
    )
    fletes_totales = int(db.execute(fletes_totales_stmt).scalar_one() or 0)
    fletes_entregados_stmt = (
        select(func.count())
        .select_from(Flete)
        .where(Flete.created_at >= since_dt, Flete.created_at < until_dt, Flete.estado == EstadoFlete.ENTREGADO)
    )
    fletes_entregados = int(db.execute(fletes_entregados_stmt).scalar_one() or 0)
    viajes_con_carga_pct = _ratio(fletes_entregados, fletes_totales)
    viajes_vacios_pct = round(max(0.0, 100.0 - viajes_con_carga_pct), 2)

    saldo_pendiente = _sum_factura_field(db, Factura.saldo_pendiente, since_dt, until_dt)
    period_days = max(1, (end_date - start_date).days + 1)
    ventas_promedio_diarias = ingresos_facturados / period_days if period_days > 0 else 0.0
    dso_dias = round((saldo_pendiente / ventas_promedio_diarias), 2) if ventas_promedio_diarias > 0 else 0.0

    items: list[DireccionDecisionGuardrailItem] = []
    bloqueos: list[str] = []

    margen_ok = margen_pct >= margen_min
    if not margen_ok:
        bloqueos.append(
            f"Margen global {margen_pct:.2f}% por debajo del mínimo {margen_min:.2f}%."
        )
    items.append(
        DireccionDecisionGuardrailItem(
            regla="margen_minimo",
            politica=f">= {margen_min:.2f}%",
            valor_actual=f"{margen_pct:.2f}%",
            estado="ok" if margen_ok else "bloqueo",
            detalle="No autorizar propuestas sin recotizar si el margen consolidado cae por debajo del umbral.",
        )
    )

    pago_ok = dso_dias <= dias_pago_max
    if not pago_ok:
        bloqueos.append(
            f"DSO {dso_dias:.2f} días supera el máximo de {dias_pago_max} días."
        )
    items.append(
        DireccionDecisionGuardrailItem(
            regla="dias_pago_maximos",
            politica=f"<= {dias_pago_max} días",
            valor_actual=f"{dso_dias:.2f} días",
            estado="ok" if pago_ok else "bloqueo",
            detalle="Flujo en riesgo: exigir anticipo o acortar plazo de pago para nuevas propuestas.",
        )
    )

    vacio_ok = viajes_vacios_pct < vacio_max
    if not vacio_ok:
        bloqueos.append(
            f"Viajes vacíos {viajes_vacios_pct:.2f}% por encima del máximo permitido {vacio_max:.2f}%."
        )
    items.append(
        DireccionDecisionGuardrailItem(
            regla="viajes_vacios_maximos",
            politica=f"< {vacio_max:.2f}%",
            valor_actual=f"{viajes_vacios_pct:.2f}%",
            estado="ok" if vacio_ok else "bloqueo",
            detalle="Sin plan de retorno no se debe aprobar expansión de rutas con baja ocupación.",
        )
    )

    missing_cost_stmt = (
        select(func.count())
        .select_from(Flete)
        .where(
            Flete.created_at >= since_dt,
            Flete.created_at < until_dt,
            func.coalesce(Flete.costo_transporte_real, Flete.costo_transporte_estimado, 0) <= 0,
        )
    )
    missing_cost = int(db.execute(missing_cost_stmt).scalar_one() or 0)
    missing_km_stmt = (
        select(func.count())
        .select_from(Flete)
        .where(Flete.created_at >= since_dt, Flete.created_at < until_dt, func.coalesce(Flete.distancia_km, 0) <= 0)
    )
    missing_km = int(db.execute(missing_km_stmt).scalar_one() or 0)
    alertas_calidad: list[str] = []
    if missing_cost > 0:
        alertas_calidad.append(
            f"{missing_cost} fletes sin costo real/estimado válido en el periodo."
        )
    if missing_km > 0:
        alertas_calidad.append(f"{missing_km} fletes sin km registrados.")

    acciones_vencidas_stmt = (
        select(func.count())
        .select_from(DireccionAccion)
        .where(
            DireccionAccion.due_date.is_not(None),
            DireccionAccion.due_date < date.today(),
            DireccionAccion.estatus.in_([AccionEstatus.PENDIENTE, AccionEstatus.EN_CURSO]),
        )
    )
    acciones_vencidas = int(db.execute(acciones_vencidas_stmt).scalar_one() or 0)
    incidencias_criticas_stmt = (
        select(func.count())
        .select_from(DireccionIncidencia)
        .where(
            DireccionIncidencia.severidad.in_([IncidenciaSeveridad.CRITICA, IncidenciaSeveridad.ALTA]),
            DireccionIncidencia.estatus != IncidenciaEstatus.RESUELTA,
        )
    )
    incidencias_criticas = int(db.execute(incidencias_criticas_stmt).scalar_one() or 0)
    alertas_disciplina: list[str] = []
    if acciones_vencidas > 0:
        alertas_disciplina.append(f"{acciones_vencidas} acciones estratégicas vencidas sin cierre.")
    if incidencias_criticas > 0:
        alertas_disciplina.append(
            f"{incidencias_criticas} incidencias críticas/altas siguen abiertas."
        )

    acciones_recomendadas: list[str] = []
    if not margen_ok:
        acciones_recomendadas.append(
            "Recotizar cartera activa para recuperar margen mínimo y frenar descuentos fuera de política."
        )
    if not pago_ok:
        acciones_recomendadas.append(
            "Condicionar nuevas ventas a anticipo o reducción de plazo de cobro."
        )
    if not vacio_ok:
        acciones_recomendadas.append(
            "Asignar plan semanal de retorno (backhaul) para reducir km vacíos."
        )
    if missing_cost > 0 or missing_km > 0:
        acciones_recomendadas.append(
            "Cerrar brechas de captura de costo/km antes del comité semanal; sin dato no hay negociación."
        )
    if acciones_vencidas > 0:
        acciones_recomendadas.append(
            "Revisar tablero de acciones y reasignar responsables con fecha de cierre."
        )

    return DireccionDecisionGuardrailsRead(
        generated_at=datetime.now(UTC).isoformat(),
        bloqueado=len(bloqueos) > 0,
        motivos_bloqueo=bloqueos,
        acciones_recomendadas=acciones_recomendadas,
        items=items,
        alertas_calidad_datos=alertas_calidad,
        alertas_disciplina=alertas_disciplina,
    )


def _build_reporte_completo(
    db: Session, user: User, start_date: date, end_date: date
) -> DireccionReporteCompletoResponse:
    _require_direccion_or_admin(user)
    since_dt, until_dt = _range_dt(start_date, end_date)

    ingresos_facturados = _sum_factura_field(db, Factura.total, since_dt, until_dt)
    cobranza_realizada = _sum_factura_field(db, Factura.total - Factura.saldo_pendiente, since_dt, until_dt)
    saldo_pendiente = _sum_factura_field(db, Factura.saldo_pendiente, since_dt, until_dt)
    costo_viaje_real = _sum_flete_field(db, func.coalesce(Flete.costo_transporte_real, Flete.costo_transporte_estimado, 0), since_dt, until_dt)
    utilidad_real = round(ingresos_facturados - costo_viaje_real, 2)
    margen_pct = _ratio_amount(utilidad_real, ingresos_facturados)
    km_totales = _sum_flete_field(db, Flete.distancia_km, since_dt, until_dt)
    ingreso_por_km = round((ingresos_facturados / km_totales), 2) if km_totales > 0 else 0.0
    costo_por_km = round((costo_viaje_real / km_totales), 2) if km_totales > 0 else 0.0
    utilidad_por_km = round(ingreso_por_km - costo_por_km, 2)
    financiero = DireccionReporteFinanciero(
        ingresos_facturados=ingresos_facturados,
        cobranza_realizada=cobranza_realizada,
        saldo_pendiente=saldo_pendiente,
        costo_viaje_real=costo_viaje_real,
        utilidad_real=utilidad_real,
        margen_pct=margen_pct,
        ingreso_por_km=ingreso_por_km,
        costo_por_km=costo_por_km,
        utilidad_por_km=utilidad_por_km,
        km_totales=km_totales,
    )

    cotizaciones_enviadas_stmt = (
        select(func.count())
        .select_from(CotizacionFlete)
        .where(
            CotizacionFlete.created_at >= since_dt,
            CotizacionFlete.created_at < until_dt,
            CotizacionFlete.estatus.in_(
                [
                    EstatusCotizacionFlete.ENVIADA,
                    EstatusCotizacionFlete.ACEPTADA,
                    EstatusCotizacionFlete.RECHAZADA,
                    EstatusCotizacionFlete.CONVERTIDA,
                ]
            ),
        )
    )
    cotizaciones_enviadas = int(db.execute(cotizaciones_enviadas_stmt).scalar_one() or 0)
    cotizaciones_convertidas_stmt = (
        select(func.count())
        .select_from(CotizacionFlete)
        .where(
            CotizacionFlete.created_at >= since_dt,
            CotizacionFlete.created_at < until_dt,
            CotizacionFlete.estatus == EstatusCotizacionFlete.CONVERTIDA,
        )
    )
    cotizaciones_convertidas = int(db.execute(cotizaciones_convertidas_stmt).scalar_one() or 0)
    cotizaciones_rechazadas_stmt = (
        select(func.count())
        .select_from(CotizacionFlete)
        .where(
            CotizacionFlete.created_at >= since_dt,
            CotizacionFlete.created_at < until_dt,
            CotizacionFlete.estatus == EstatusCotizacionFlete.RECHAZADA,
        )
    )
    cotizaciones_rechazadas = int(db.execute(cotizaciones_rechazadas_stmt).scalar_one() or 0)
    ingreso_cotizado_stmt = (
        select(func.coalesce(func.sum(CotizacionFlete.precio_venta_sugerido), 0))
        .where(
            CotizacionFlete.created_at >= since_dt,
            CotizacionFlete.created_at < until_dt,
            CotizacionFlete.estatus.in_(
                [
                    EstatusCotizacionFlete.ENVIADA,
                    EstatusCotizacionFlete.ACEPTADA,
                    EstatusCotizacionFlete.RECHAZADA,
                    EstatusCotizacionFlete.CONVERTIDA,
                ]
            ),
        )
    )
    ingreso_cotizado = round(_safe_float(db.execute(ingreso_cotizado_stmt).scalar_one()), 2)
    ingreso_convertido_stmt = (
        select(func.coalesce(func.sum(CotizacionFlete.precio_venta_sugerido), 0))
        .where(
            CotizacionFlete.created_at >= since_dt,
            CotizacionFlete.created_at < until_dt,
            CotizacionFlete.estatus == EstatusCotizacionFlete.CONVERTIDA,
        )
    )
    ingreso_convertido = round(_safe_float(db.execute(ingreso_convertido_stmt).scalar_one()), 2)
    clientes_convertidores_stmt = (
        select(func.count(func.distinct(CotizacionFlete.cliente_id)))
        .where(
            CotizacionFlete.created_at >= since_dt,
            CotizacionFlete.created_at < until_dt,
            CotizacionFlete.estatus == EstatusCotizacionFlete.CONVERTIDA,
            CotizacionFlete.cliente_id.is_not(None),
        )
    )
    conversion = DireccionReporteConversion(
        cotizaciones_enviadas=cotizaciones_enviadas,
        cotizaciones_convertidas=cotizaciones_convertidas,
        cotizaciones_rechazadas=cotizaciones_rechazadas,
        tasa_conversion_pct=_ratio(cotizaciones_convertidas, cotizaciones_enviadas),
        tasa_rechazo_pct=_ratio(cotizaciones_rechazadas, cotizaciones_enviadas),
        ingreso_cotizado=ingreso_cotizado,
        ingreso_convertido=ingreso_convertido,
        conversion_por_valor_pct=_ratio_amount(ingreso_convertido, ingreso_cotizado),
        clientes_convertedores_unicos=int(db.execute(clientes_convertidores_stmt).scalar_one() or 0),
    )

    facturas_totales_stmt = (
        select(func.count()).select_from(Factura).where(Factura.created_at >= since_dt, Factura.created_at < until_dt)
    )
    facturas_totales = int(db.execute(facturas_totales_stmt).scalar_one() or 0)
    facturas_cobradas_stmt = (
        select(func.count())
        .select_from(Factura)
        .where(Factura.created_at >= since_dt, Factura.created_at < until_dt, Factura.estatus == EstatusFactura.COBRADA)
    )
    facturas_cobradas = int(db.execute(facturas_cobradas_stmt).scalar_one() or 0)
    vencida_stmt = (
        select(func.coalesce(func.sum(Factura.saldo_pendiente), 0))
        .where(
            Factura.created_at >= since_dt,
            Factura.created_at < until_dt,
            Factura.fecha_vencimiento.is_not(None),
            Factura.fecha_vencimiento < end_date,
            Factura.saldo_pendiente > 0,
        )
    )
    cartera_vencida = round(_safe_float(db.execute(vencida_stmt).scalar_one()), 2)
    facturado_total = ingresos_facturados
    cobrado_total = cobranza_realizada
    period_days = max(1, (end_date - start_date).days + 1)
    ventas_promedio_diarias = facturado_total / period_days if period_days > 0 else 0.0
    dso_dias = round((saldo_pendiente / ventas_promedio_diarias), 2) if ventas_promedio_diarias > 0 else None
    cartera_rows_stmt = (
        select(Factura.fecha_vencimiento, Factura.saldo_pendiente)
        .where(Factura.created_at >= since_dt, Factura.created_at < until_dt, Factura.saldo_pendiente > 0)
    )
    buckets = {
        "0_30": {"label": "0-30", "monto": 0.0, "facturas": 0},
        "31_60": {"label": "31-60", "monto": 0.0, "facturas": 0},
        "61_90": {"label": "61-90", "monto": 0.0, "facturas": 0},
        "91_mas": {"label": "91+", "monto": 0.0, "facturas": 0},
    }
    for fecha_vencimiento, saldo in db.execute(cartera_rows_stmt).all():
        saldo_float = _safe_float(saldo)
        dias = 0
        if fecha_vencimiento:
            dias = (end_date - fecha_vencimiento).days
        if dias <= 30:
            key = "0_30"
        elif dias <= 60:
            key = "31_60"
        elif dias <= 90:
            key = "61_90"
        else:
            key = "91_mas"
        buckets[key]["monto"] += saldo_float
        buckets[key]["facturas"] += 1
    antiguedad = [
        DireccionBucketAntiguedad(bucket=b["label"], monto=round(float(b["monto"]), 2), facturas=int(b["facturas"]))
        for b in buckets.values()
    ]
    top3_concentracion_stmt = (
        select(Factura.cliente_id, func.coalesce(func.sum(Factura.saldo_pendiente), 0).label("saldo"))
        .where(Factura.created_at >= since_dt, Factura.created_at < until_dt, Factura.saldo_pendiente > 0)
        .group_by(Factura.cliente_id)
        .order_by(func.coalesce(func.sum(Factura.saldo_pendiente), 0).desc())
        .limit(3)
    )
    top3_saldo = 0.0
    for _, saldo in db.execute(top3_concentracion_stmt).all():
        top3_saldo += _safe_float(saldo)
    cartera = DireccionReporteCartera(
        cuentas_por_cobrar=saldo_pendiente,
        cartera_vencida=cartera_vencida,
        cartera_vencida_pct=_ratio_amount(cartera_vencida, saldo_pendiente),
        dso_dias=dso_dias,
        indice_recuperacion_pct=_ratio_amount(cobrado_total, facturado_total),
        concentracion_top3_pct=_ratio_amount(top3_saldo, saldo_pendiente),
        antiguedad=antiguedad,
    )

    fletes_totales_stmt = (
        select(func.count()).select_from(Flete).where(Flete.created_at >= since_dt, Flete.created_at < until_dt)
    )
    fletes_entregados_stmt = (
        select(func.count())
        .select_from(Flete)
        .where(Flete.created_at >= since_dt, Flete.created_at < until_dt, Flete.estado == EstadoFlete.ENTREGADO)
    )
    fletes_totales = int(db.execute(fletes_totales_stmt).scalar_one() or 0)
    fletes_entregados = int(db.execute(fletes_entregados_stmt).scalar_one() or 0)
    facturas_emitidas_stmt = (
        select(func.count())
        .select_from(Factura)
        .where(
            Factura.created_at >= since_dt,
            Factura.created_at < until_dt,
            Factura.estatus.in_([EstatusFactura.EMITIDA, EstatusFactura.ENVIADA, EstatusFactura.PARCIAL, EstatusFactura.COBRADA]),
        )
    )
    facturas_emitidas = int(db.execute(facturas_emitidas_stmt).scalar_one() or 0)
    dashboard = get_dashboard_direccion(db=db, user=user, desde=start_date, hasta=end_date)
    productividad = DireccionReporteProductividad(
        fletes_totales=fletes_totales,
        fletes_entregados=fletes_entregados,
        facturas_emitidas=facturas_emitidas,
        facturas_cobradas=facturas_cobradas,
        viajes_con_carga_pct=_ratio(fletes_entregados, fletes_totales),
        despacho_a_factura_pct=dashboard.embudo.despacho_a_factura_pct,
        cumplimiento_cobranza_pct=_ratio(facturas_cobradas, facturas_totales),
    )

    guardrails = _build_decision_guardrails(db=db, user=user, start_date=start_date, end_date=end_date)
    alertas: list[str] = []
    if financiero.utilidad_por_km <= 0:
        alertas.append("Utilidad por km en negativo o en cero.")
    elif financiero.utilidad_por_km < 2:
        alertas.append("Utilidad por km fragil (< 2 MXN).")
    if cartera.cartera_vencida_pct >= 20:
        alertas.append("Cartera vencida arriba de 20%.")
    if conversion.tasa_conversion_pct < 20:
        alertas.append("Conversion comercial menor al 20%.")
    if productividad.viajes_con_carga_pct < 80:
        alertas.append("Utilizacion con carga menor al 80%.")
    for msg in guardrails.motivos_bloqueo:
        alertas.append(f"Guardrail bloqueado: {msg}")
    for msg in guardrails.alertas_calidad_datos:
        alertas.append(f"Calidad de datos: {msg}")
    for msg in guardrails.alertas_disciplina:
        alertas.append(f"Disciplina operativa: {msg}")
    if not alertas:
        estado_sostenibilidad = "sostenible"
        mensaje_sostenibilidad = "Operacion rentable, repetible y bajo control."
    elif len(alertas) <= 2:
        estado_sostenibilidad = "en_riesgo"
        mensaje_sostenibilidad = "Se detectan alertas moderadas; ajustar en comite semanal."
    else:
        estado_sostenibilidad = "critico"
        mensaje_sostenibilidad = "Riesgo alto de sostenibilidad; tomar acciones inmediatas."
    sostenibilidad = DireccionReporteSostenibilidad(
        estado=estado_sostenibilidad,
        mensaje=mensaje_sostenibilidad,
        alertas=alertas,
        semaforo=dashboard.semaforo,
    )

    top_clientes_stmt = (
        select(
            Factura.cliente_id,
            func.coalesce(func.max(Cliente.razon_social), "Cliente sin nombre").label("cliente"),
            func.coalesce(func.sum(Factura.total), 0).label("ingresos"),
            func.coalesce(func.sum(Flete.costo_transporte_real), 0).label("costo_real"),
            func.coalesce(func.sum(Flete.costo_transporte_estimado), 0).label("costo_est"),
            func.count(Factura.id).label("facturas"),
        )
        .join(Flete, Flete.id == Factura.flete_id, isouter=True)
        .join(Cliente, Cliente.id == Factura.cliente_id, isouter=True)
        .where(Factura.created_at >= since_dt, Factura.created_at < until_dt)
        .group_by(Factura.cliente_id)
        .order_by(func.coalesce(func.sum(Factura.total), 0).desc())
        .limit(5)
    )
    top_clientes_rentabilidad: list[DireccionReporteClienteRentabilidad] = []
    for cliente_id, cliente, ingresos, costo_real, costo_est, facturas_cliente in db.execute(top_clientes_stmt).all():
        ingresos_f = _safe_float(ingresos)
        costo_f = _safe_float(costo_real) if _safe_float(costo_real) > 0 else _safe_float(costo_est)
        utilidad_f = round(ingresos_f - costo_f, 2)
        top_clientes_rentabilidad.append(
            DireccionReporteClienteRentabilidad(
                cliente_id=cliente_id,
                cliente=cliente,
                ingresos=round(ingresos_f, 2),
                costo=round(costo_f, 2),
                utilidad=utilidad_f,
                margen_pct=_ratio_amount(utilidad_f, ingresos_f),
                fletes=int(facturas_cliente or 0),
            )
        )

    return DireccionReporteCompletoResponse(
        desde=start_date,
        hasta=end_date,
        financiero=financiero,
        conversion=conversion,
        cartera=cartera,
        productividad=productividad,
        sostenibilidad=sostenibilidad,
        top_clientes_rentabilidad=top_clientes_rentabilidad,
        decision_guardrails=guardrails,
    )


def _incidencia_to_read(row: DireccionIncidencia) -> DireccionIncidenciaRead:
    return DireccionIncidenciaRead(
        id=row.id,
        titulo=row.titulo,
        modulo=row.modulo,
        severidad=row.severidad.value,
        estatus=row.estatus.value,
        fecha_detectada=row.fecha_detectada,
        detalle=row.detalle,
        responsable=row.responsable,
        resuelta_at=row.resuelta_at.isoformat() if row.resuelta_at else None,
        created_at=row.created_at.isoformat(),
        updated_at=row.updated_at.isoformat(),
    )


def _accion_to_read(row: DireccionAccion) -> DireccionAccionRead:
    return DireccionAccionRead(
        id=row.id,
        week_start=row.week_start,
        week_end=row.week_end,
        titulo=row.titulo,
        descripcion=row.descripcion,
        owner=row.owner,
        due_date=row.due_date,
        impacto=row.impacto,
        estatus=row.estatus.value,
        created_at=row.created_at.isoformat(),
        updated_at=row.updated_at.isoformat(),
    )


def _parse_severidad(value: str) -> IncidenciaSeveridad:
    try:
        return IncidenciaSeveridad((value or "").strip().lower())
    except ValueError as exc:
        raise HTTPException(status_code=422, detail="Severidad invalida.") from exc


def _parse_estatus_incidencia(value: str) -> IncidenciaEstatus:
    try:
        return IncidenciaEstatus((value or "").strip().lower())
    except ValueError as exc:
        raise HTTPException(status_code=422, detail="Estatus de incidencia invalido.") from exc


def _parse_estatus_accion(value: str) -> AccionEstatus:
    try:
        return AccionEstatus((value or "").strip().lower())
    except ValueError as exc:
        raise HTTPException(status_code=422, detail="Estatus de accion invalido.") from exc


def _list_incidencias_rows(db: Session, start_date: date, end_date: date) -> list[DireccionIncidencia]:
    stmt = (
        select(DireccionIncidencia)
        .where(
            DireccionIncidencia.fecha_detectada >= start_date,
            DireccionIncidencia.fecha_detectada <= end_date,
        )
        .order_by(DireccionIncidencia.fecha_detectada.desc(), DireccionIncidencia.id.desc())
    )
    return list(db.execute(stmt).scalars().all())


def _list_acciones_rows(db: Session, start_date: date, end_date: date) -> list[DireccionAccion]:
    stmt = (
        select(DireccionAccion)
        .where(DireccionAccion.week_start >= start_date, DireccionAccion.week_end <= end_date)
        .order_by(DireccionAccion.week_start.desc(), DireccionAccion.id.desc())
    )
    return list(db.execute(stmt).scalars().all())


def _week_bounds(ref: date) -> tuple[date, date]:
    start = ref - timedelta(days=ref.weekday())
    end = start + timedelta(days=6)
    return start, end


def _default_owner_for_guardrail(regla: str) -> str:
    key = (regla or "").strip().lower()
    if "margen" in key:
        return "comercial"
    if "pago" in key or "dso" in key:
        return "finanzas"
    if "vacio" in key or "retorno" in key:
        return "operaciones"
    if "calidad" in key or "dato" in key:
        return "control_operativo"
    return "direccion"


def _create_or_get_weekly_action(
    db: Session,
    *,
    week_start: date,
    week_end: date,
    title: str,
    description: str | None,
    owner: str,
    due_date: date | None,
    impacto: str | None,
    allowed_open_statuses: tuple[AccionEstatus, ...] = (AccionEstatus.PENDIENTE, AccionEstatus.EN_CURSO),
) -> tuple[DireccionAccion, bool]:
    stmt = (
        select(DireccionAccion)
        .where(
            DireccionAccion.week_start == week_start,
            DireccionAccion.week_end == week_end,
            func.lower(DireccionAccion.titulo) == title.lower(),
            DireccionAccion.estatus.in_(list(allowed_open_statuses)),
        )
        .order_by(DireccionAccion.id.desc())
        .limit(1)
    )
    existing = db.execute(stmt).scalar_one_or_none()
    if existing is not None:
        return existing, False
    row = DireccionAccion(
        week_start=week_start,
        week_end=week_end,
        titulo=title,
        descripcion=description,
        owner=owner,
        due_date=due_date,
        impacto=impacto,
        estatus=AccionEstatus.PENDIENTE,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row, True


def _baseline_from_description(desc: str | None) -> dict[str, float]:
    text = str(desc or "")
    marker = "BASELINE::"
    if marker not in text:
        return {}
    raw = text.split(marker, 1)[1].strip()
    try:
        payload = json.loads(raw)
        if isinstance(payload, dict):
            out: dict[str, float] = {}
            for k, v in payload.items():
                try:
                    out[str(k)] = float(v)
                except Exception:
                    continue
            return out
    except Exception:
        return {}
    return {}


def _impact_closure_from_description(desc: str | None) -> tuple[float, str | None]:
    text = str(desc or "")
    marker = "CIERRE::"
    if marker not in text:
        return 0.0, None
    raw = text.split(marker, 1)[1].strip()
    try:
        payload = json.loads(raw)
        if isinstance(payload, dict):
            monto = float(payload.get("impacto_realizado_mxn", 0.0) or 0.0)
            comentario = str(payload.get("comentario_cierre") or "").strip() or None
            return max(0.0, monto), comentario
    except Exception:
        return 0.0, None
    return 0.0, None


@router.get(
    "/dashboard",
    response_model=DireccionDashboardResponse,
    summary="Tablero ejecutivo para dirección",
)
def get_dashboard_direccion(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user_jwt),
    desde: date | None = Query(default=None),
    hasta: date | None = Query(default=None),
) -> DireccionDashboardResponse:
    _require_direccion_or_admin(user)
    start_date, end_date = _clamp_range(desde, hasta)
    since_dt, until_dt = _range_dt(start_date, end_date)

    fletes = _count_in_range(db, Flete, Flete.created_at, since_dt, until_dt)
    ordenes_servicio = _count_in_range(db, OrdenServicio, OrdenServicio.created_at, since_dt, until_dt)
    asignaciones = _count_in_range(db, Asignacion, Asignacion.created_at, since_dt, until_dt)
    despachos = _count_in_range(db, Despacho, Despacho.created_at, since_dt, until_dt)
    facturas = _count_in_range(db, Factura, Factura.created_at, since_dt, until_dt)

    despachos_cerrados_stmt = (
        select(func.count())
        .select_from(Despacho)
        .where(
            Despacho.created_at >= since_dt,
            Despacho.created_at < until_dt,
            Despacho.estatus == EstadoDespacho.CERRADO,
        )
    )
    despachos_cerrados = int(db.execute(despachos_cerrados_stmt).scalar_one() or 0)

    facturas_emitidas_stmt = (
        select(func.count())
        .select_from(Factura)
        .where(
            Factura.created_at >= since_dt,
            Factura.created_at < until_dt,
            Factura.estatus.in_([EstatusFactura.EMITIDA, EstatusFactura.ENVIADA, EstatusFactura.PARCIAL, EstatusFactura.COBRADA]),
        )
    )
    facturas_emitidas = int(db.execute(facturas_emitidas_stmt).scalar_one() or 0)

    incidencias_stmt = (
        select(func.count())
        .select_from(DespachoEvento)
        .where(
            DespachoEvento.created_at >= since_dt,
            DespachoEvento.created_at < until_dt,
            DespachoEvento.tipo_evento == TipoEventoDespacho.INCIDENCIA,
        )
    )
    incidencias = int(db.execute(incidencias_stmt).scalar_one() or 0)

    os_vinculadas_flete_stmt = (
        select(func.count())
        .select_from(OrdenServicio)
        .where(
            OrdenServicio.created_at >= since_dt,
            OrdenServicio.created_at < until_dt,
            OrdenServicio.flete_id.is_not(None),
        )
    )
    os_vinculadas_flete = int(db.execute(os_vinculadas_flete_stmt).scalar_one() or 0)

    despachos_con_asignacion_stmt = (
        select(func.count())
        .select_from(Despacho)
        .where(
            Despacho.created_at >= since_dt,
            Despacho.created_at < until_dt,
            Despacho.id_asignacion.is_not(None),
        )
    )
    despachos_con_asignacion = int(db.execute(despachos_con_asignacion_stmt).scalar_one() or 0)

    facturas_con_despacho_stmt = (
        select(func.count())
        .select_from(Factura)
        .join(OrdenServicio, OrdenServicio.id == Factura.orden_servicio_id, isouter=True)
        .where(
            Factura.created_at >= since_dt,
            Factura.created_at < until_dt,
            OrdenServicio.despacho_id.is_not(None),
        )
    )
    facturas_con_despacho = int(db.execute(facturas_con_despacho_stmt).scalar_one() or 0)

    flete_factura_pairs_stmt = (
        select(Flete.created_at, Factura.created_at)
        .join(Factura, Factura.flete_id == Flete.id)
        .where(Factura.created_at >= since_dt, Factura.created_at < until_dt)
    )
    flete_factura_pairs = list(db.execute(flete_factura_pairs_stmt).all())

    orden_despacho_pairs_stmt = (
        select(OrdenServicio.created_at, Despacho.created_at)
        .join(Despacho, Despacho.id_despacho == OrdenServicio.despacho_id)
        .where(Despacho.created_at >= since_dt, Despacho.created_at < until_dt)
    )
    orden_despacho_pairs = list(db.execute(orden_despacho_pairs_stmt).all())

    despacho_factura_pairs_stmt = (
        select(Despacho.created_at, Factura.created_at)
        .join(OrdenServicio, OrdenServicio.despacho_id == Despacho.id_despacho)
        .join(Factura, Factura.orden_servicio_id == OrdenServicio.id)
        .where(Factura.created_at >= since_dt, Factura.created_at < until_dt)
    )
    despacho_factura_pairs = list(db.execute(despacho_factura_pairs_stmt).all())

    embudo = DireccionEmbudo(
        fletes_a_os_pct=_ratio(os_vinculadas_flete, fletes),
        os_a_asignacion_pct=_ratio(asignaciones, ordenes_servicio),
        asignacion_a_despacho_pct=_ratio(despachos_con_asignacion, asignaciones),
        despacho_a_factura_pct=_ratio(facturas_con_despacho, despachos),
    )

    tiempos = DireccionTiemposCiclo(
        flete_a_factura_horas=_avg_hours_from_pairs(flete_factura_pairs),
        orden_a_despacho_horas=_avg_hours_from_pairs(orden_despacho_pairs),
        despacho_a_factura_horas=_avg_hours_from_pairs(despacho_factura_pairs),
    )

    semaforo = DireccionSemaforo(
        operacion="verde" if despachos_cerrados >= max(1, round(despachos * 0.6)) else ("amarillo" if despachos_cerrados > 0 else "rojo"),
        sistema="verde",
        dato="verde" if incidencias <= 2 else ("amarillo" if incidencias <= 5 else "rojo"),
        cobranza="verde"
        if embudo.despacho_a_factura_pct >= 70
        else ("amarillo" if embudo.despacho_a_factura_pct >= 40 else "rojo"),
    )

    return DireccionDashboardResponse(
        desde=start_date,
        hasta=end_date,
        resumen=DireccionKpiResumen(
            fletes=fletes,
            ordenes_servicio=ordenes_servicio,
            asignaciones=asignaciones,
            despachos=despachos,
            despachos_cerrados=despachos_cerrados,
            facturas=facturas,
            facturas_emitidas=facturas_emitidas,
            incidencias_despacho=incidencias,
        ),
        embudo=embudo,
        tiempos=tiempos,
        semaforo=semaforo,
    )


@router.get("/incidencias", response_model=list[DireccionIncidenciaRead], summary="Listar incidencias dirección")
def list_incidencias(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user_jwt),
    desde: date | None = Query(default=None),
    hasta: date | None = Query(default=None),
) -> list[DireccionIncidenciaRead]:
    _require_direccion_or_admin(user)
    start_date, end_date = _clamp_range(desde, hasta)
    rows = _list_incidencias_rows(db, start_date, end_date)
    return [_incidencia_to_read(x) for x in rows]


@router.post("/incidencias", response_model=DireccionIncidenciaRead, summary="Crear incidencia dirección")
def create_incidencia(
    payload: DireccionIncidenciaCreate,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user_jwt),
) -> DireccionIncidenciaRead:
    _require_direccion_or_admin(user)
    row = DireccionIncidencia(
        titulo=payload.titulo.strip(),
        modulo=payload.modulo.strip(),
        severidad=_parse_severidad(payload.severidad),
        estatus=_parse_estatus_incidencia(payload.estatus),
        fecha_detectada=payload.fecha_detectada,
        detalle=payload.detalle,
        responsable=payload.responsable,
    )
    if row.estatus == IncidenciaEstatus.RESUELTA:
        row.resuelta_at = datetime.utcnow()
    db.add(row)
    db.commit()
    db.refresh(row)
    write_audit_log(
        db,
        request,
        entity="direccion_incidencia",
        entity_id=row.id,
        action="create",
        after=model_to_dict(row),
    )
    return _incidencia_to_read(row)


@router.patch("/incidencias/{incidencia_id}", response_model=DireccionIncidenciaRead, summary="Actualizar incidencia dirección")
def update_incidencia(
    incidencia_id: int,
    payload: DireccionIncidenciaUpdate,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user_jwt),
) -> DireccionIncidenciaRead:
    _require_direccion_or_admin(user)
    row = db.get(DireccionIncidencia, incidencia_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Incidencia no encontrada.")
    before = model_to_dict(row)
    data = payload.model_dump(exclude_unset=True)
    if "titulo" in data:
        row.titulo = data["titulo"].strip()
    if "modulo" in data:
        row.modulo = data["modulo"].strip()
    if "severidad" in data:
        row.severidad = _parse_severidad(data["severidad"])
    if "estatus" in data:
        new_status = _parse_estatus_incidencia(data["estatus"])
        row.estatus = new_status
        if new_status == IncidenciaEstatus.RESUELTA and row.resuelta_at is None:
            row.resuelta_at = datetime.utcnow()
        if new_status != IncidenciaEstatus.RESUELTA:
            row.resuelta_at = None
    if "fecha_detectada" in data:
        row.fecha_detectada = data["fecha_detectada"]
    if "detalle" in data:
        row.detalle = data["detalle"]
    if "responsable" in data:
        row.responsable = data["responsable"]
    db.add(row)
    db.commit()
    db.refresh(row)
    write_audit_log(
        db,
        request,
        entity="direccion_incidencia",
        entity_id=incidencia_id,
        action="update",
        before=before,
        after=model_to_dict(row),
    )
    return _incidencia_to_read(row)


@router.get("/acciones", response_model=list[DireccionAccionRead], summary="Listar acciones dirección")
def list_acciones(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user_jwt),
    week_start: date | None = Query(default=None),
    week_end: date | None = Query(default=None),
) -> list[DireccionAccionRead]:
    _require_direccion_or_admin(user)
    start_date, end_date = _clamp_range(week_start, week_end)
    rows = _list_acciones_rows(db, start_date, end_date)
    return [_accion_to_read(x) for x in rows]


@router.post("/acciones", response_model=DireccionAccionRead, summary="Crear acción semanal dirección")
def create_accion(
    payload: DireccionAccionCreate,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user_jwt),
) -> DireccionAccionRead:
    _require_direccion_or_admin(user)
    if payload.week_start > payload.week_end:
        raise HTTPException(status_code=422, detail="week_start no puede ser mayor que week_end.")
    row = DireccionAccion(
        week_start=payload.week_start,
        week_end=payload.week_end,
        titulo=payload.titulo.strip(),
        descripcion=payload.descripcion,
        owner=payload.owner.strip(),
        due_date=payload.due_date,
        impacto=payload.impacto,
        estatus=_parse_estatus_accion(payload.estatus),
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    write_audit_log(
        db,
        request,
        entity="direccion_accion",
        entity_id=row.id,
        action="create",
        after=model_to_dict(row),
    )
    return _accion_to_read(row)


@router.post(
    "/acciones/from-guardrail",
    response_model=DireccionAccionRead,
    summary="Crear acción correctiva desde guardrail (idempotente semanal)",
)
def create_accion_from_guardrail(
    payload: DireccionAccionFromGuardrailCreate,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user_jwt),
) -> DireccionAccionRead:
    _require_direccion_or_admin(user)
    ws, we = _week_bounds(date.today())
    owner = payload.owner.strip() if payload.owner and payload.owner.strip() else _default_owner_for_guardrail(payload.regla)
    titulo = f"[GUARDRAIL] {payload.regla.strip().lower()}"
    due = date.today() + timedelta(days=int(payload.dias_compromiso))
    current_guardrails = _build_decision_guardrails(db=db, user=user, start_date=ws, end_date=we)
    item = next((x for x in current_guardrails.items if x.regla == payload.regla.strip().lower()), None)
    baseline_payload = {
        "margen_pct": 0.0,
        "dso_dias": 0.0,
        "viajes_vacios_pct": 0.0,
    }
    try:
        # extrae baseline de la lectura semanal para medir before/after sin nuevas tablas.
        if item and "margen" in item.regla:
            baseline_payload["margen_pct"] = float(str(item.valor_actual).replace("%", "").strip())
        if item and ("pago" in item.regla or "dso" in item.regla):
            baseline_payload["dso_dias"] = float(str(item.valor_actual).replace("días", "").strip())
        if item and ("vacios" in item.regla or "retorno" in item.regla):
            baseline_payload["viajes_vacios_pct"] = float(str(item.valor_actual).replace("%", "").strip())
    except Exception:
        pass
    row, created = _create_or_get_weekly_action(
        db,
        week_start=ws,
        week_end=we,
        title=titulo,
        description=(
            f"Acción correctiva automática por guardrail. Motivo: {payload.motivo.strip()}\n"
            f"BASELINE::{json.dumps(baseline_payload, ensure_ascii=True)}"
        ),
        owner=owner,
        due_date=due,
        impacto=payload.impacto.strip() if payload.impacto else "Mitigar riesgo financiero-operativo",
    )
    if not created:
        return _accion_to_read(row)
    write_audit_log(
        db,
        request,
        entity="direccion_accion",
        entity_id=row.id,
        action="create_guardrail",
        after=model_to_dict(row),
        meta={"regla": payload.regla.strip().lower()},
    )
    return _accion_to_read(row)


@router.patch("/acciones/{accion_id}", response_model=DireccionAccionRead, summary="Actualizar acción semanal dirección")
def update_accion(
    accion_id: int,
    payload: DireccionAccionUpdate,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user_jwt),
) -> DireccionAccionRead:
    _require_direccion_or_admin(user)
    row = db.get(DireccionAccion, accion_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Accion no encontrada.")
    before = model_to_dict(row)
    data = payload.model_dump(exclude_unset=True)
    if "week_start" in data:
        row.week_start = data["week_start"]
    if "week_end" in data:
        row.week_end = data["week_end"]
    if row.week_start > row.week_end:
        raise HTTPException(status_code=422, detail="week_start no puede ser mayor que week_end.")
    if "titulo" in data:
        row.titulo = data["titulo"].strip()
    if "descripcion" in data:
        row.descripcion = data["descripcion"]
    if "owner" in data:
        row.owner = data["owner"].strip()
    if "due_date" in data:
        row.due_date = data["due_date"]
    if "impacto" in data:
        row.impacto = data["impacto"]
    if "estatus" in data:
        row.estatus = _parse_estatus_accion(data["estatus"])
    db.add(row)
    db.commit()
    db.refresh(row)
    write_audit_log(
        db,
        request,
        entity="direccion_accion",
        entity_id=accion_id,
        action="update",
        before=before,
        after=model_to_dict(row),
    )
    return _accion_to_read(row)


@router.post(
    "/acciones/from-recommendation",
    response_model=DireccionAccionRead,
    summary="Crear acción correctiva desde recomendación destruye-margen",
)
def create_accion_from_recommendation(
    payload: DireccionAccionFromRecommendationCreate,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user_jwt),
) -> DireccionAccionRead:
    _require_direccion_or_admin(user)
    source_type = (payload.source_type or "").strip().lower()
    if source_type not in {"cliente", "ruta"}:
        raise HTTPException(status_code=422, detail="source_type debe ser 'cliente' o 'ruta'.")
    ws, we = _week_bounds(date.today())
    source_name = payload.source_name.strip()
    accion = payload.accion_sugerida.strip()
    title = f"[DESTRUYE-MARGEN:{source_type}] {source_name}"
    owner = (payload.owner or "").strip() or ("comercial" if source_type == "cliente" else "operaciones")
    due = date.today() + timedelta(days=int(payload.dias_compromiso))
    description = (
        f"Acción correctiva automática por ranking destruye-margen ({source_type}). "
        f"Recomendación: {accion}"
    )
    row, created = _create_or_get_weekly_action(
        db,
        week_start=ws,
        week_end=we,
        title=title,
        description=description,
        owner=owner,
        due_date=due,
        impacto=(payload.impacto.strip() if payload.impacto else "Recuperar margen operativo/comercial"),
    )
    if not created:
        return _accion_to_read(row)
    write_audit_log(
        db,
        request,
        entity="direccion_accion",
        entity_id=row.id,
        action="create_recommendation",
        after=model_to_dict(row),
        meta={"source_type": source_type, "source_name": source_name},
    )
    return _accion_to_read(row)


@router.post(
    "/acciones/{accion_id}/cerrar-impacto",
    response_model=DireccionAccionRead,
    summary="Cerrar acción con evidencia de impacto realizado",
)
def close_accion_with_impact(
    accion_id: int,
    payload: DireccionAccionCerrarImpactoCreate,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user_jwt),
) -> DireccionAccionRead:
    _require_direccion_or_admin(user)
    row = db.get(DireccionAccion, accion_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Accion no encontrada.")
    before = model_to_dict(row)
    desc_base = str(row.descripcion or "")
    if "CIERRE::" in desc_base:
        desc_base = desc_base.split("CIERRE::", 1)[0].rstrip()
    closure = {
        "impacto_realizado_mxn": float(payload.impacto_realizado_mxn),
        "comentario_cierre": payload.comentario_cierre.strip(),
        "closed_at": datetime.now(UTC).isoformat(),
        "closed_by": user.username,
    }
    row.descripcion = (f"{desc_base}\n" if desc_base else "") + f"CIERRE::{json.dumps(closure, ensure_ascii=True)}"
    if payload.marcar_completada:
        row.estatus = AccionEstatus.COMPLETADA
    db.add(row)
    db.commit()
    db.refresh(row)
    write_audit_log(
        db,
        request,
        entity="direccion_accion",
        entity_id=accion_id,
        action="close_impact",
        before=before,
        after=model_to_dict(row),
        meta={"impacto_realizado_mxn": float(payload.impacto_realizado_mxn)},
    )
    return _accion_to_read(row)


@router.get(
    "/acciones/seguimiento",
    response_model=DireccionAccionSeguimientoRead,
    summary="Seguimiento de cumplimiento de acciones estratégicas",
)
def get_acciones_seguimiento(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user_jwt),
    week_start: date | None = Query(default=None),
    week_end: date | None = Query(default=None),
) -> DireccionAccionSeguimientoRead:
    _require_direccion_or_admin(user)
    start_date, end_date = _clamp_range(week_start, week_end)
    rows = _list_acciones_rows(db, start_date, end_date)
    total = len(rows)
    pendientes = sum(1 for a in rows if a.estatus == AccionEstatus.PENDIENTE)
    en_curso = sum(1 for a in rows if a.estatus == AccionEstatus.EN_CURSO)
    completadas = sum(1 for a in rows if a.estatus == AccionEstatus.COMPLETADA)
    canceladas = sum(1 for a in rows if a.estatus == AccionEstatus.CANCELADA)
    vencidas_abiertas = sum(
        1
        for a in rows
        if a.due_date is not None and a.due_date < date.today() and a.estatus in {AccionEstatus.PENDIENTE, AccionEstatus.EN_CURSO}
    )
    cumplimiento_pct = _ratio(completadas + canceladas, total) if total > 0 else 0.0
    completadas_en_tiempo = sum(
        1
        for a in rows
        if a.estatus == AccionEstatus.COMPLETADA
        and a.due_date is not None
        and a.updated_at is not None
        and a.updated_at.date() <= a.due_date
    )
    cumplimiento_tiempo_pct = _ratio(completadas_en_tiempo, completadas) if completadas > 0 else 0.0
    mensaje = (
        f"Seguimiento semanal: {completadas} completadas, {pendientes + en_curso} abiertas y {vencidas_abiertas} vencidas."
        if total > 0
        else "Sin acciones registradas para el periodo."
    )
    return DireccionAccionSeguimientoRead(
        desde=start_date,
        hasta=end_date,
        total=total,
        pendientes=pendientes,
        en_curso=en_curso,
        completadas=completadas,
        canceladas=canceladas,
        vencidas_abiertas=vencidas_abiertas,
        cumplimiento_pct=cumplimiento_pct,
        cumplimiento_en_tiempo_pct=cumplimiento_tiempo_pct,
        mensaje=mensaje,
    )


@router.get(
    "/acciones/impacto",
    response_model=DireccionAccionImpactoRead,
    summary="Comparativo before/after de acciones correctivas de guardrail",
)
def get_acciones_impacto(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user_jwt),
    week_start: date | None = Query(default=None),
    week_end: date | None = Query(default=None),
) -> DireccionAccionImpactoRead:
    _require_direccion_or_admin(user)
    start_date, end_date = _clamp_range(week_start, week_end)
    rows = _list_acciones_rows(db, start_date, end_date)
    current_guardrails = _build_decision_guardrails(db=db, user=user, start_date=start_date, end_date=end_date)
    current_map = {x.regla: x for x in current_guardrails.items}
    items: list[DireccionAccionImpactoItem] = []
    impacto_total = 0.0
    impacto_total_realizado = 0.0
    for row in rows:
        if not row.titulo.startswith("[GUARDRAIL]"):
            continue
        regla = row.titulo.replace("[GUARDRAIL]", "", 1).strip().lower()
        baseline = _baseline_from_description(row.descripcion)
        impacto_realizado_mxn, comentario_cierre = _impact_closure_from_description(row.descripcion)
        curr = current_map.get(regla)
        before_valor = "—"
        current_valor = curr.valor_actual if curr is not None else "—"
        delta = "—"
        impacto_estimado = 0.0
        try:
            if "margen" in regla:
                b = float(baseline.get("margen_pct", 0.0))
                c = float(str(current_valor).replace("%", "").strip()) if current_valor != "—" else b
                before_valor = f"{b:.2f}%"
                current_valor = f"{c:.2f}%"
                d = c - b
                delta = f"{d:+.2f} pts"
                impacto_estimado = round(max(0.0, d) * 1200.0, 2)
            elif "pago" in regla or "dso" in regla:
                b = float(baseline.get("dso_dias", 0.0))
                c = float(str(current_valor).replace("días", "").strip()) if current_valor != "—" else b
                before_valor = f"{b:.2f} días"
                current_valor = f"{c:.2f} días"
                d = c - b
                delta = f"{d:+.2f} días"
                impacto_estimado = round(max(0.0, -d) * 900.0, 2)
            elif "vacios" in regla or "retorno" in regla:
                b = float(baseline.get("viajes_vacios_pct", 0.0))
                c = float(str(current_valor).replace("%", "").strip()) if current_valor != "—" else b
                before_valor = f"{b:.2f}%"
                current_valor = f"{c:.2f}%"
                d = c - b
                delta = f"{d:+.2f} pts"
                impacto_estimado = round(max(0.0, -d) * 800.0, 2)
        except Exception:
            pass
        impacto_total += impacto_estimado
        impacto_total_realizado += max(0.0, impacto_realizado_mxn)
        items.append(
            DireccionAccionImpactoItem(
                accion_id=row.id,
                titulo=row.titulo,
                regla=regla,
                estado=row.estatus.value,
                owner=row.owner,
                before_valor=before_valor,
                current_valor=current_valor,
                delta=delta,
                impacto_estimado_mxn=impacto_estimado,
                impacto_realizado_mxn=impacto_realizado_mxn,
                comentario_cierre=comentario_cierre,
            )
        )
    return DireccionAccionImpactoRead(
        generated_at=datetime.now(UTC).isoformat(),
        items=items,
        impacto_total_estimado_mxn=round(impacto_total, 2),
        impacto_total_realizado_mxn=round(impacto_total_realizado, 2),
    )


@router.get(
    "/acciones/impacto/roi",
    response_model=DireccionAccionRoiRead,
    summary="Top acciones por ROI real (realizado vs estimado)",
)
def get_acciones_impacto_roi(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user_jwt),
    week_start: date | None = Query(default=None),
    week_end: date | None = Query(default=None),
    limit: int = Query(default=10, ge=1, le=50),
) -> DireccionAccionRoiRead:
    _require_direccion_or_admin(user)
    impacto = get_acciones_impacto(
        db=db,
        user=user,
        week_start=week_start,
        week_end=week_end,
    )
    rows: list[DireccionAccionRoiItem] = []
    for it in impacto.items:
        est = float(it.impacto_estimado_mxn or 0.0)
        real = float(it.impacto_realizado_mxn or 0.0)
        roi = round((real / est) * 100.0, 2) if est > 0 else None
        rows.append(
            DireccionAccionRoiItem(
                accion_id=it.accion_id,
                regla=it.regla,
                owner=it.owner,
                estatus=it.estado,
                impacto_estimado_mxn=est,
                impacto_realizado_mxn=real,
                roi_real_pct=roi,
            )
        )
    rows.sort(
        key=lambda x: (
            x.roi_real_pct if x.roi_real_pct is not None else -1.0,
            x.impacto_realizado_mxn,
        ),
        reverse=True,
    )
    return DireccionAccionRoiRead(
        generated_at=datetime.now(UTC).isoformat(),
        items=rows[:limit],
    )


@router.get(
    "/reportes/destruye-margen",
    response_model=DireccionDestruyeMargenRead,
    summary="Top clientes y rutas que destruyen margen con acción sugerida",
)
def get_reporte_destruye_margen(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user_jwt),
    desde: date | None = Query(default=None),
    hasta: date | None = Query(default=None),
    limit: int = Query(default=5, ge=1, le=20),
) -> DireccionDestruyeMargenRead:
    _require_direccion_or_admin(user)
    start_date, end_date = _clamp_range(desde, hasta)
    since_dt, until_dt = _range_dt(start_date, end_date)
    margen_min = 20.0

    clientes_stmt = (
        select(
            Factura.cliente_id,
            func.coalesce(func.max(Cliente.razon_social), "Cliente sin nombre").label("cliente"),
            func.coalesce(func.sum(Factura.total), 0).label("ingresos"),
            func.coalesce(func.sum(func.coalesce(Flete.costo_transporte_real, Flete.costo_transporte_estimado, 0)), 0).label("costo"),
        )
        .join(Flete, Flete.id == Factura.flete_id, isouter=True)
        .join(Cliente, Cliente.id == Factura.cliente_id, isouter=True)
        .where(Factura.created_at >= since_dt, Factura.created_at < until_dt)
        .group_by(Factura.cliente_id)
    )
    clientes_rows = list(db.execute(clientes_stmt).all())
    clientes_items: list[DireccionDestruyeMargenClienteItem] = []
    for cliente_id, cliente, ingresos, costo in clientes_rows:
        ingresos_f = _safe_float(ingresos)
        costo_f = _safe_float(costo)
        utilidad_f = round(ingresos_f - costo_f, 2)
        margen = _ratio_amount(utilidad_f, ingresos_f)
        if margen >= margen_min:
            continue
        accion = (
            "Renegociar tarifa o plazo de pago; no aceptar descuentos sin recuperación."
            if margen >= 0
            else "Congelar nuevas órdenes hasta rediseñar costo/ruta del cliente."
        )
        clientes_items.append(
            DireccionDestruyeMargenClienteItem(
                cliente_id=cliente_id,
                cliente=cliente,
                ingresos=round(ingresos_f, 2),
                costo=round(costo_f, 2),
                utilidad=utilidad_f,
                margen_pct=margen,
                accion_sugerida=accion,
            )
        )
    clientes_items.sort(key=lambda x: x.margen_pct)
    clientes_items = clientes_items[:limit]

    rutas_stmt = (
        select(
            func.coalesce(Viaje.origen, "N/D").label("origen"),
            func.coalesce(Viaje.destino, "N/D").label("destino"),
            func.count(Flete.id).label("fletes"),
            func.coalesce(func.sum(Flete.precio_venta), 0).label("ingresos"),
            func.coalesce(func.sum(func.coalesce(Flete.costo_transporte_real, Flete.costo_transporte_estimado, 0)), 0).label("costo"),
        )
        .select_from(Flete)
        .join(Viaje, Viaje.id == Flete.viaje_id, isouter=True)
        .where(Flete.created_at >= since_dt, Flete.created_at < until_dt)
        .group_by(func.coalesce(Viaje.origen, "N/D"), func.coalesce(Viaje.destino, "N/D"))
    )
    rutas_rows = list(db.execute(rutas_stmt).all())
    rutas_items: list[DireccionDestruyeMargenRutaItem] = []
    for origen, destino, fletes_n, ingresos, costo in rutas_rows:
        ingresos_f = _safe_float(ingresos)
        costo_f = _safe_float(costo)
        utilidad_f = round(ingresos_f - costo_f, 2)
        margen = _ratio_amount(utilidad_f, ingresos_f)
        if margen >= margen_min:
            continue
        accion = (
            "Buscar retorno/backhaul y optimizar asignación para subir ocupación."
            if margen >= 0
            else "Pausar ruta no rentable y recotizar estructura completa."
        )
        rutas_items.append(
            DireccionDestruyeMargenRutaItem(
                ruta=f"{origen} -> {destino}",
                fletes=int(fletes_n or 0),
                ingresos=round(ingresos_f, 2),
                costo=round(costo_f, 2),
                utilidad=utilidad_f,
                margen_pct=margen,
                accion_sugerida=accion,
            )
        )
    rutas_items.sort(key=lambda x: x.margen_pct)
    rutas_items = rutas_items[:limit]

    return DireccionDestruyeMargenRead(
        generated_at=datetime.now(UTC).isoformat(),
        clientes=clientes_items,
        rutas=rutas_items,
    )


@router.get(
    "/reportes/estado-guerra",
    response_model=DireccionEstadoGuerraRead,
    summary="Estado de guerra: comité ejecutivo en una sola vista",
)
def get_estado_guerra(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user_jwt),
    desde: date | None = Query(default=None),
    hasta: date | None = Query(default=None),
) -> DireccionEstadoGuerraRead:
    _require_direccion_or_admin(user)
    start_date, end_date = _clamp_range(desde, hasta)
    guardrails = _build_decision_guardrails(db=db, user=user, start_date=start_date, end_date=end_date)
    seguimiento = get_acciones_seguimiento(
        db=db,
        user=user,
        week_start=start_date,
        week_end=end_date,
    )
    impacto = get_acciones_impacto(
        db=db,
        user=user,
        week_start=start_date,
        week_end=end_date,
    )
    roi = get_acciones_impacto_roi(
        db=db,
        user=user,
        week_start=start_date,
        week_end=end_date,
        limit=5,
    )
    destruye = get_reporte_destruye_margen(
        db=db,
        user=user,
        desde=start_date,
        hasta=end_date,
        limit=3,
    )
    bloqueos = len(guardrails.motivos_bloqueo)
    acciones_vencidas = int(seguimiento.vencidas_abiertas)
    riesgo_estimado = round(float(impacto.impacto_total_estimado_mxn or 0.0), 2)
    recuperado = round(float(impacto.impacto_total_realizado_mxn or 0.0), 2)
    roi_vals = [x.roi_real_pct for x in roi.items if x.roi_real_pct is not None]
    roi_avg = round(sum(roi_vals) / len(roi_vals), 2) if roi_vals else 0.0
    if bloqueos == 0 and acciones_vencidas == 0:
        semaforo = "verde"
    elif bloqueos <= 2 and acciones_vencidas <= 2:
        semaforo = "amarillo"
    else:
        semaforo = "rojo"
    prioridades: list[str] = []
    for msg in guardrails.motivos_bloqueo[:3]:
        prioridades.append(f"Bloqueo: {msg}")
    for it in roi.items[:2]:
        prioridades.append(
            f"ROI foco #{it.accion_id}: {it.regla} ({it.roi_real_pct if it.roi_real_pct is not None else 'N/A'}%)."
        )
    for it in destruye.clientes[:2]:
        prioridades.append(f"Cliente crítico: {it.cliente} ({it.margen_pct:.2f}%).")
    plan = [
        "Lunes: revisar bloqueos activos y asignar due date.",
        "Martes: ejecutar recotizaciones y condiciones de cobro.",
        "Miércoles: optimizar rutas con mayor destrucción de margen.",
        "Jueves: validar cierres con impacto realizado.",
        "Viernes: comité de guerra y snapshot semanal.",
    ]
    return DireccionEstadoGuerraRead(
        generated_at=datetime.now(UTC).isoformat(),
        semaforo_general=semaforo,
        bloqueos_activos=bloqueos,
        acciones_vencidas=acciones_vencidas,
        riesgo_mensual_estimado_mxn=riesgo_estimado,
        recuperacion_realizada_mxn=recuperado,
        roi_real_promedio_pct=roi_avg,
        top_prioridades=prioridades,
        plan_semanal=plan,
    )


@router.get(
    "/export/estado-guerra.csv",
    summary="Exportar brief de comité (estado de guerra)",
)
def export_estado_guerra_csv(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user_jwt),
    desde: date | None = Query(default=None),
    hasta: date | None = Query(default=None),
) -> Response:
    _require_direccion_or_admin(user)
    start_date, end_date = _clamp_range(desde, hasta)
    data = get_estado_guerra(db=db, user=user, desde=start_date, hasta=end_date)
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["kpi", "valor"])
    writer.writerow(["semaforo_general", data.semaforo_general])
    writer.writerow(["bloqueos_activos", data.bloqueos_activos])
    writer.writerow(["acciones_vencidas", data.acciones_vencidas])
    writer.writerow(["riesgo_mensual_estimado_mxn", data.riesgo_mensual_estimado_mxn])
    writer.writerow(["recuperacion_realizada_mxn", data.recuperacion_realizada_mxn])
    writer.writerow(["roi_real_promedio_pct", data.roi_real_promedio_pct])
    for idx, x in enumerate(data.top_prioridades, start=1):
        writer.writerow([f"prioridad_{idx}", x])
    for idx, x in enumerate(data.plan_semanal, start=1):
        writer.writerow([f"plan_{idx}", x])
    filename = f"direccion_estado_guerra_{start_date.isoformat()}_{end_date.isoformat()}.csv"
    return Response(
        content=buf.getvalue(),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/resumen-semanal", summary="Resumen automático semanal de dirección")
def get_resumen_semanal(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user_jwt),
    desde: date | None = Query(default=None),
    hasta: date | None = Query(default=None),
) -> dict:
    _require_direccion_or_admin(user)
    start_date, end_date = _clamp_range(desde, hasta)
    dashboard = get_dashboard_direccion(db=db, user=user, desde=start_date, hasta=end_date)
    incidencias = _list_incidencias_rows(db, start_date, end_date)
    acciones = _list_acciones_rows(db, start_date, end_date)

    criticas_abiertas = sum(
        1
        for i in incidencias
        if i.severidad in {IncidenciaSeveridad.ALTA, IncidenciaSeveridad.CRITICA}
        and i.estatus != IncidenciaEstatus.RESUELTA
    )
    acciones_pendientes = sum(
        1 for a in acciones if a.estatus in {AccionEstatus.PENDIENTE, AccionEstatus.EN_CURSO}
    )
    acciones_total = len(acciones)
    acciones_completadas = sum(1 for a in acciones if a.estatus == AccionEstatus.COMPLETADA)
    acciones_vencidas = sum(
        1
        for a in acciones
        if a.due_date is not None and a.due_date < date.today() and a.estatus in {AccionEstatus.PENDIENTE, AccionEstatus.EN_CURSO}
    )

    message = (
        f"Semana {start_date.isoformat()} a {end_date.isoformat()}: "
        f"{dashboard.resumen.despachos_cerrados} despachos cerrados, "
        f"{dashboard.resumen.facturas_emitidas} facturas emitidas y "
        f"conversión despacho->factura de {dashboard.embudo.despacho_a_factura_pct:.2f}%."
    )

    return {
        "desde": start_date,
        "hasta": end_date,
        "mensaje": message,
        "riesgos": {
            "incidencias_criticas_abiertas": criticas_abiertas,
            "acciones_pendientes": acciones_pendientes,
            "acciones_total": acciones_total,
            "acciones_completadas": acciones_completadas,
            "acciones_vencidas": acciones_vencidas,
            "cumplimiento_acciones_pct": _ratio(acciones_completadas, acciones_total),
        },
        "semaforo": dashboard.semaforo.model_dump(),
        "embudo": dashboard.embudo.model_dump(),
        "tiempos": dashboard.tiempos.model_dump(),
    }


@router.get("/historico-semanal", summary="Tendencia y semáforo histórico semanal")
def get_historico_semanal(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user_jwt),
    semanas: int = Query(default=8, ge=2, le=26),
) -> dict:
    _require_direccion_or_admin(user)
    today = date.today()
    current_start, _ = _week_bounds(today)
    rows: list[dict] = []
    for i in range(semanas - 1, -1, -1):
        week_start = current_start - timedelta(days=7 * i)
        week_end = week_start + timedelta(days=6)
        dash = get_dashboard_direccion(db=db, user=user, desde=week_start, hasta=week_end)
        rows.append(
            {
                "week_start": week_start,
                "week_end": week_end,
                "despachos_cerrados": dash.resumen.despachos_cerrados,
                "facturas_emitidas": dash.resumen.facturas_emitidas,
                "despacho_a_factura_pct": dash.embudo.despacho_a_factura_pct,
                "semaforo": dash.semaforo.model_dump(),
            }
        )
    return {"semanas": semanas, "items": rows}


@router.get(
    "/reportes/completo",
    response_model=DireccionReporteCompletoResponse,
    summary="Sistema integral de reportes de dirección",
)
def get_reporte_completo(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user_jwt),
    desde: date | None = Query(default=None),
    hasta: date | None = Query(default=None),
) -> DireccionReporteCompletoResponse:
    _require_direccion_or_admin(user)
    start_date, end_date = _clamp_range(desde, hasta)
    return _build_reporte_completo(db=db, user=user, start_date=start_date, end_date=end_date)


@router.get(
    "/reportes/decision-guardrails",
    response_model=DireccionDecisionGuardrailsRead,
    summary="Guardrails de decisión para proteger rentabilidad, flujo y disciplina",
)
def get_decision_guardrails(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user_jwt),
    desde: date | None = Query(default=None),
    hasta: date | None = Query(default=None),
) -> DireccionDecisionGuardrailsRead:
    _require_direccion_or_admin(user)
    start_date, end_date = _clamp_range(desde, hasta)
    return _build_decision_guardrails(db=db, user=user, start_date=start_date, end_date=end_date)


@router.get(
    "/reportes/committee/snapshots",
    response_model=DireccionSemanalSnapshotListResponse,
    summary="Listar snapshots semanales del reporte integral (comité)",
)
def list_committee_snapshots(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user_jwt),
    limit: int = Query(default=24, ge=1, le=104),
) -> DireccionSemanalSnapshotListResponse:
    _require_direccion_or_admin(user)
    stmt = (
        select(DireccionSemanalReporteSnapshot)
        .order_by(DireccionSemanalReporteSnapshot.week_start.desc())
        .limit(limit)
    )
    rows = list(db.execute(stmt).scalars().all())
    items = [
        DireccionSemanalSnapshotItem(
            id=r.id,
            week_start=r.week_start,
            week_end=r.week_end,
            created_at=r.created_at.isoformat(),
            created_by_user_id=r.created_by_user_id,
        )
        for r in rows
    ]
    return DireccionSemanalSnapshotListResponse(items=items)


@router.get(
    "/reportes/committee/snapshot",
    summary="Obtener snapshot por semana ISO o el más reciente",
)
def get_committee_snapshot(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user_jwt),
    week_start: date | None = Query(default=None, description="Cualquier fecha dentro de la semana ISO (lun-dom)"),
) -> dict:
    _require_direccion_or_admin(user)
    if week_start is not None:
        ws, we = _week_bounds(week_start)
        stmt = select(DireccionSemanalReporteSnapshot).where(DireccionSemanalReporteSnapshot.week_start == ws)
        row = db.execute(stmt).scalar_one_or_none()
    else:
        stmt = (
            select(DireccionSemanalReporteSnapshot)
            .order_by(DireccionSemanalReporteSnapshot.week_start.desc())
            .limit(1)
        )
        row = db.execute(stmt).scalar_one_or_none()
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Snapshot no encontrado.")
    try:
        payload = json.loads(row.payload_json or "{}")
    except Exception:
        payload = {}
    return {
        "id": row.id,
        "week_start": row.week_start,
        "week_end": row.week_end,
        "created_at": row.created_at.isoformat(),
        "created_by_user_id": row.created_by_user_id,
        "reporte": payload,
    }


def upsert_committee_snapshot_for_week(
    db: Session,
    user: User,
    request: Request | None,
    ref: date,
    *,
    audit_action: str = "create",
) -> dict:
    """Idempotente por `week_start` ISO (alineado con `_week_bounds`)."""
    ws, we = _week_bounds(ref)
    stmt = select(DireccionSemanalReporteSnapshot).where(DireccionSemanalReporteSnapshot.week_start == ws)
    existing = db.execute(stmt).scalar_one_or_none()
    if existing is not None:
        try:
            payload = json.loads(existing.payload_json or "{}")
        except Exception:
            payload = {}
        return {
            "id": existing.id,
            "week_start": existing.week_start,
            "week_end": existing.week_end,
            "created": False,
            "created_at": existing.created_at.isoformat(),
            "created_by_user_id": existing.created_by_user_id,
            "reporte": payload,
        }
    report = _build_reporte_completo(db=db, user=user, start_date=ws, end_date=we)
    dump = report.model_dump(mode="json")
    row = DireccionSemanalReporteSnapshot(
        week_start=ws,
        week_end=we,
        payload_json=json.dumps(dump, ensure_ascii=True),
        created_by_user_id=user.id,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    write_audit_log(
        db,
        request,
        entity="direccion_committee_snapshot",
        entity_id=str(ws),
        action=audit_action,
        after={"week_start": str(ws), "week_end": str(we), "snapshot_id": row.id},
    )
    return {
        "id": row.id,
        "week_start": ws,
        "week_end": we,
        "created": True,
        "created_at": row.created_at.isoformat(),
        "created_by_user_id": row.created_by_user_id,
        "reporte": dump,
    }


@router.post(
    "/reportes/committee/snapshot",
    summary="Crear snapshot semanal del reporte integral (idempotente por semana ISO)",
)
def create_committee_snapshot(
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user_jwt),
    week_start: date | None = Query(
        default=None,
        description="Inicio de semana deseado; si se omite se usa la semana ISO de hoy",
    ),
) -> dict:
    _require_direccion_or_admin(user)
    return upsert_committee_snapshot_for_week(db, user, request, week_start or date.today())


@router.get(
    "/reportes/thresholds",
    response_model=DireccionThresholdsRead,
    summary="Obtener umbrales de reporte integral por usuario/rol",
)
def get_reporte_thresholds(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user_jwt),
) -> DireccionThresholdsRead:
    _require_direccion_or_admin(user)
    win_enabled = settings.DIRECCION_THRESHOLD_EDIT_WINDOW_ENABLED
    edit_allowed, edit_reason = _threshold_user_edit_allowed(user)
    role_name = (user.role.name if user.role else "").strip().lower()
    user_override_allowed = _get_role_override_policy(db, role_name)
    source, cfg_row = _get_threshold_config_for_user(db, user)
    if cfg_row is None:
        return DireccionThresholdsRead(
            source="default",
            thresholds=DireccionThresholds(**_default_thresholds_dict()),
            history=[],
            user_override_allowed=user_override_allowed,
            edit_window_enabled=win_enabled,
            edit_allowed=edit_allowed,
            edit_blocked_reason=edit_reason,
        )
    try:
        cfg_payload = json.loads(cfg_row.config_json or "{}")
    except Exception:
        cfg_payload = {}
    history_rows_stmt = (
        select(DireccionKpiConfigHistory)
        .where(DireccionKpiConfigHistory.config_id == cfg_row.id)
        .order_by(DireccionKpiConfigHistory.id.desc())
        .limit(20)
    )
    history_rows = list(db.execute(history_rows_stmt).scalars().all())
    history: list[DireccionThresholdHistoryRead] = []
    for row in history_rows:
        changes = []
        try:
            parsed = json.loads(row.changes_json or "[]")
            if isinstance(parsed, list):
                changes = [str(x) for x in parsed]
        except Exception:
            changes = []
        history.append(
            DireccionThresholdHistoryRead(
                id=row.id,
                mode=row.mode,
                changes=changes,
                created_at=row.created_at.isoformat(),
            )
        )
    return DireccionThresholdsRead(
        source=source.replace("_locked", ""),
        thresholds=_to_thresholds(cfg_payload),
        history=history,
        user_override_allowed=user_override_allowed,
        edit_window_enabled=win_enabled,
        edit_allowed=edit_allowed,
        edit_blocked_reason=edit_reason,
    )


@router.put(
    "/reportes/thresholds",
    response_model=DireccionThresholdsRead,
    summary="Actualizar umbrales de reporte integral para usuario actual",
)
def update_reporte_thresholds(
    payload: DireccionThresholdsUpdate,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user_jwt),
) -> DireccionThresholdsRead:
    _require_direccion_or_admin(user)
    role_name = (user.role.name if user.role else "").strip().lower()
    if not _get_role_override_policy(db, role_name):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="La política del rol bloquea override de usuario.",
        )
    edit_allowed, edit_reason = _threshold_user_edit_allowed(user)
    if not edit_allowed:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=edit_reason or "Edición de umbrales no permitida en este momento.",
        )
    scope_type = "user"
    scope_value = f"user:{user.id}"
    stmt = select(DireccionKpiConfig).where(
        DireccionKpiConfig.scope_type == scope_type,
        DireccionKpiConfig.scope_value == scope_value,
    )
    cfg_row = db.execute(stmt).scalar_one_or_none()
    before_cfg = _default_thresholds_dict()
    if cfg_row is not None:
        try:
            before_cfg = {**before_cfg, **(json.loads(cfg_row.config_json or "{}"))}
        except Exception:
            before_cfg = _default_thresholds_dict()
    next_cfg = payload.thresholds.model_dump()
    if cfg_row is None:
        cfg_row = DireccionKpiConfig(
            scope_type=scope_type,
            scope_value=scope_value,
            config_json=json.dumps(next_cfg, ensure_ascii=True),
            updated_by_user_id=user.id,
        )
        db.add(cfg_row)
        db.flush()
    else:
        cfg_row.config_json = json.dumps(next_cfg, ensure_ascii=True)
        cfg_row.updated_by_user_id = user.id
        db.add(cfg_row)
    history = DireccionKpiConfigHistory(
        config_id=cfg_row.id,
        mode=(payload.mode or "manual").strip().lower()[:32],
        changes_json=json.dumps(_thresholds_diff(before_cfg, next_cfg), ensure_ascii=True),
        created_by_user_id=user.id,
    )
    db.add(history)
    db.commit()
    write_audit_log(
        db,
        request,
        entity="direccion_thresholds",
        entity_id=f"user:{user.id}",
        action="update",
        before=before_cfg,
        after=next_cfg,
        meta={"mode": (payload.mode or "manual").strip().lower()[:32]},
    )
    return get_reporte_thresholds(db=db, user=user)


@router.get(
    "/reportes/thresholds/role/{role_name}",
    response_model=DireccionThresholdsRead,
    summary="Obtener umbrales de reporte integral para un rol",
)
def get_reporte_thresholds_by_role(
    role_name: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user_jwt),
) -> DireccionThresholdsRead:
    _require_direccion_or_admin(user)
    role_norm = (role_name or "").strip().lower()
    if not role_norm:
        raise HTTPException(status_code=422, detail="role_name es requerido.")
    role_stmt = select(Role).where(func.lower(Role.name) == role_norm)
    role = db.execute(role_stmt).scalar_one_or_none()
    if role is None:
        raise HTTPException(status_code=404, detail="Rol no encontrado.")
    scope_value = f"role:{role_norm}"
    stmt = select(DireccionKpiConfig).where(
        DireccionKpiConfig.scope_type == "role",
        DireccionKpiConfig.scope_value == scope_value,
    )
    cfg_row = db.execute(stmt).scalar_one_or_none()
    if cfg_row is None:
        return DireccionThresholdsRead(
            source="default",
            thresholds=DireccionThresholds(**_default_thresholds_dict()),
            history=[],
        )
    try:
        cfg_payload = json.loads(cfg_row.config_json or "{}")
    except Exception:
        cfg_payload = {}
    history_rows_stmt = (
        select(DireccionKpiConfigHistory)
        .where(DireccionKpiConfigHistory.config_id == cfg_row.id)
        .order_by(DireccionKpiConfigHistory.id.desc())
        .limit(20)
    )
    history_rows = list(db.execute(history_rows_stmt).scalars().all())
    history: list[DireccionThresholdHistoryRead] = []
    for row in history_rows:
        try:
            parsed = json.loads(row.changes_json or "[]")
            changes = [str(x) for x in parsed] if isinstance(parsed, list) else []
        except Exception:
            changes = []
        history.append(
            DireccionThresholdHistoryRead(
                id=row.id,
                mode=row.mode,
                changes=changes,
                created_at=row.created_at.isoformat(),
            )
        )
    return DireccionThresholdsRead(
        source="role",
        thresholds=_to_thresholds(cfg_payload),
        history=history,
    )


@router.put(
    "/reportes/thresholds/role/{role_name}",
    response_model=DireccionThresholdsRead,
    summary="Actualizar umbrales de reporte integral para un rol",
)
def update_reporte_thresholds_by_role(
    role_name: str,
    payload: DireccionThresholdsUpdate,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user_jwt),
) -> DireccionThresholdsRead:
    _require_admin(user)
    role_norm = (role_name or "").strip().lower()
    if not role_norm:
        raise HTTPException(status_code=422, detail="role_name es requerido.")
    role_stmt = select(Role).where(func.lower(Role.name) == role_norm)
    role = db.execute(role_stmt).scalar_one_or_none()
    if role is None:
        raise HTTPException(status_code=404, detail="Rol no encontrado.")
    scope_type = "role"
    scope_value = f"role:{role_norm}"
    stmt = select(DireccionKpiConfig).where(
        DireccionKpiConfig.scope_type == scope_type,
        DireccionKpiConfig.scope_value == scope_value,
    )
    cfg_row = db.execute(stmt).scalar_one_or_none()
    before_cfg = _default_thresholds_dict()
    if cfg_row is not None:
        try:
            before_cfg = {**before_cfg, **(json.loads(cfg_row.config_json or "{}"))}
        except Exception:
            before_cfg = _default_thresholds_dict()
    next_cfg = payload.thresholds.model_dump()
    if cfg_row is None:
        cfg_row = DireccionKpiConfig(
            scope_type=scope_type,
            scope_value=scope_value,
            config_json=json.dumps(next_cfg, ensure_ascii=True),
            updated_by_user_id=user.id,
        )
        db.add(cfg_row)
        db.flush()
    else:
        cfg_row.config_json = json.dumps(next_cfg, ensure_ascii=True)
        cfg_row.updated_by_user_id = user.id
        db.add(cfg_row)
    history = DireccionKpiConfigHistory(
        config_id=cfg_row.id,
        mode=(payload.mode or "manual").strip().lower()[:32],
        changes_json=json.dumps(_thresholds_diff(before_cfg, next_cfg), ensure_ascii=True),
        created_by_user_id=user.id,
    )
    db.add(history)
    db.commit()
    write_audit_log(
        db,
        request,
        entity="direccion_thresholds",
        entity_id=f"role:{role_norm}",
        action="update",
        before=before_cfg,
        after=next_cfg,
        meta={"mode": (payload.mode or "manual").strip().lower()[:32]},
    )
    return get_reporte_thresholds_by_role(role_name=role_norm, db=db, user=user)


@router.get(
    "/reportes/thresholds/policy/{role_name}",
    response_model=DireccionThresholdPolicyRead,
    summary="Consultar política de override por rol",
)
def get_reporte_threshold_policy(
    role_name: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user_jwt),
) -> DireccionThresholdPolicyRead:
    _require_direccion_or_admin(user)
    role_norm = (role_name or "").strip().lower()
    if not role_norm:
        raise HTTPException(status_code=422, detail="role_name es requerido.")
    role_stmt = select(Role).where(func.lower(Role.name) == role_norm)
    role = db.execute(role_stmt).scalar_one_or_none()
    if role is None:
        raise HTTPException(status_code=404, detail="Rol no encontrado.")
    return DireccionThresholdPolicyRead(
        role_name=role_norm,
        user_override_allowed=_get_role_override_policy(db, role_norm),
    )


@router.put(
    "/reportes/thresholds/policy/{role_name}",
    response_model=DireccionThresholdPolicyRead,
    summary="Actualizar política de override por rol",
)
def update_reporte_threshold_policy(
    role_name: str,
    payload: DireccionThresholdPolicyUpdate,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user_jwt),
) -> DireccionThresholdPolicyRead:
    _require_admin(user)
    role_norm = (role_name or "").strip().lower()
    if not role_norm:
        raise HTTPException(status_code=422, detail="role_name es requerido.")
    role_stmt = select(Role).where(func.lower(Role.name) == role_norm)
    role = db.execute(role_stmt).scalar_one_or_none()
    if role is None:
        raise HTTPException(status_code=404, detail="Rol no encontrado.")
    scope_type = "policy"
    scope_value = f"role:{role_norm}"
    stmt = select(DireccionKpiConfig).where(
        DireccionKpiConfig.scope_type == scope_type,
        DireccionKpiConfig.scope_value == scope_value,
    )
    row = db.execute(stmt).scalar_one_or_none()
    before = {"user_override_allowed": _get_role_override_policy(db, role_norm)}
    cfg_payload = {"user_override_allowed": bool(payload.user_override_allowed)}
    if row is None:
        row = DireccionKpiConfig(
            scope_type=scope_type,
            scope_value=scope_value,
            config_json=json.dumps(cfg_payload, ensure_ascii=True),
            updated_by_user_id=user.id,
        )
        db.add(row)
    else:
        row.config_json = json.dumps(cfg_payload, ensure_ascii=True)
        row.updated_by_user_id = user.id
        db.add(row)
    db.commit()
    write_audit_log(
        db,
        request,
        entity="direccion_threshold_policy",
        entity_id=f"role:{role_norm}",
        action="update",
        before=before,
        after=cfg_payload,
    )
    return DireccionThresholdPolicyRead(
        role_name=role_norm,
        user_override_allowed=bool(payload.user_override_allowed),
    )


@router.get(
    "/reportes/thresholds/governance",
    summary="Vista consolidada de gobierno de umbrales por rol",
)
def get_reporte_threshold_governance(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user_jwt),
) -> dict:
    _require_admin(user)
    roles = list(db.execute(select(Role).order_by(Role.name.asc())).scalars().all())
    items: list[dict] = []
    for role in roles:
        role_norm = (role.name or "").strip().lower()
        cfg_stmt = select(DireccionKpiConfig).where(
            DireccionKpiConfig.scope_type == "role",
            DireccionKpiConfig.scope_value == f"role:{role_norm}",
        )
        cfg = db.execute(cfg_stmt).scalar_one_or_none()
        items.append(
            {
                "role_name": role_norm,
                "has_role_thresholds": cfg is not None,
                "user_override_allowed": _get_role_override_policy(db, role_norm),
            }
        )
    return {"items": items}


@router.get(
    "/reportes/thresholds/governance/users",
    summary="Vista de cumplimiento por usuario (hereda vs override)",
)
def get_reporte_threshold_governance_users(
    role_name: str | None = Query(default=None),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user_jwt),
) -> dict:
    _require_admin(user)
    users_stmt = select(User).join(Role, Role.id == User.role_id).order_by(User.id.asc())
    rows = list(db.execute(users_stmt).scalars().all())
    role_filter = (role_name or "").strip().lower()
    items: list[dict] = []
    for u in rows:
        rname = (u.role.name if u.role else "").strip().lower()
        if role_filter and rname != role_filter:
            continue
        user_scope = f"user:{u.id}"
        user_cfg_stmt = select(DireccionKpiConfig).where(
            DireccionKpiConfig.scope_type == "user",
            DireccionKpiConfig.scope_value == user_scope,
        )
        has_user_override = db.execute(user_cfg_stmt).scalar_one_or_none() is not None
        policy_allows = _get_role_override_policy(db, rname)
        if has_user_override and policy_allows:
            effective_source = "user"
        else:
            role_cfg_stmt = select(DireccionKpiConfig).where(
                DireccionKpiConfig.scope_type == "role",
                DireccionKpiConfig.scope_value == f"role:{rname}",
            )
            has_role_cfg = db.execute(role_cfg_stmt).scalar_one_or_none() is not None
            effective_source = "role" if has_role_cfg else "default"
        items.append(
            {
                "user_id": u.id,
                "username": u.username,
                "role_name": rname,
                "is_active": bool(u.is_active),
                "has_user_override": has_user_override,
                "user_override_allowed": policy_allows,
                "effective_source": effective_source,
            }
        )
    return {"items": items}


@router.post(
    "/reportes/thresholds/role/{role_name}/clear-user-overrides",
    summary="Limpiar overrides de usuarios de un rol",
)
def clear_user_overrides_for_role(
    role_name: str,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user_jwt),
) -> dict:
    _require_admin(user)
    role_norm = (role_name or "").strip().lower()
    if not role_norm:
        raise HTTPException(status_code=422, detail="role_name es requerido.")
    role_stmt = select(Role).where(func.lower(Role.name) == role_norm)
    role = db.execute(role_stmt).scalar_one_or_none()
    if role is None:
        raise HTTPException(status_code=404, detail="Rol no encontrado.")
    users_stmt = select(User).where(User.role_id == role.id)
    users = list(db.execute(users_stmt).scalars().all())
    deleted = 0
    for u in users:
        user_scope = f"user:{u.id}"
        cfg_stmt = select(DireccionKpiConfig).where(
            DireccionKpiConfig.scope_type == "user",
            DireccionKpiConfig.scope_value == user_scope,
        )
        cfg = db.execute(cfg_stmt).scalar_one_or_none()
        if cfg is not None:
            db.delete(cfg)
            deleted += 1
    db.commit()
    write_audit_log(
        db,
        request,
        entity="direccion_thresholds",
        entity_id=f"role:{role_norm}",
        action="clear_user_overrides",
        before={"role_name": role_norm},
        after={"deleted_user_overrides": deleted},
    )
    return {"role_name": role_norm, "deleted_user_overrides": deleted}


@router.get("/export/dashboard.csv", summary="Exportar dashboard de dirección a CSV")
def export_dashboard_csv(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user_jwt),
    desde: date | None = Query(default=None),
    hasta: date | None = Query(default=None),
) -> Response:
    _require_direccion_or_admin(user)
    start_date, end_date = _clamp_range(desde, hasta)
    dashboard = get_dashboard_direccion(db=db, user=user, desde=start_date, hasta=end_date)
    summary = get_resumen_semanal(db=db, user=user, desde=start_date, hasta=end_date)

    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["desde", "hasta", "fletes", "ordenes_servicio", "asignaciones", "despachos", "despachos_cerrados", "facturas", "facturas_emitidas", "incidencias_despacho", "fletes_a_os_pct", "os_a_asignacion_pct", "asignacion_a_despacho_pct", "despacho_a_factura_pct", "flete_a_factura_horas", "orden_a_despacho_horas", "despacho_a_factura_horas", "semaforo_operacion", "semaforo_sistema", "semaforo_dato", "semaforo_cobranza", "incidencias_criticas_abiertas", "acciones_pendientes"])
    writer.writerow(
        [
            dashboard.desde.isoformat(),
            dashboard.hasta.isoformat(),
            dashboard.resumen.fletes,
            dashboard.resumen.ordenes_servicio,
            dashboard.resumen.asignaciones,
            dashboard.resumen.despachos,
            dashboard.resumen.despachos_cerrados,
            dashboard.resumen.facturas,
            dashboard.resumen.facturas_emitidas,
            dashboard.resumen.incidencias_despacho,
            dashboard.embudo.fletes_a_os_pct,
            dashboard.embudo.os_a_asignacion_pct,
            dashboard.embudo.asignacion_a_despacho_pct,
            dashboard.embudo.despacho_a_factura_pct,
            dashboard.tiempos.flete_a_factura_horas,
            dashboard.tiempos.orden_a_despacho_horas,
            dashboard.tiempos.despacho_a_factura_horas,
            dashboard.semaforo.operacion,
            dashboard.semaforo.sistema,
            dashboard.semaforo.dato,
            dashboard.semaforo.cobranza,
            summary["riesgos"]["incidencias_criticas_abiertas"],
            summary["riesgos"]["acciones_pendientes"],
        ]
    )
    filename = f"direccion_dashboard_{start_date.isoformat()}_{end_date.isoformat()}.csv"
    return Response(
        content=buf.getvalue(),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/export/incidencias.csv", summary="Exportar incidencias de dirección a CSV")
def export_incidencias_csv(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user_jwt),
    desde: date | None = Query(default=None),
    hasta: date | None = Query(default=None),
) -> Response:
    _require_direccion_or_admin(user)
    start_date, end_date = _clamp_range(desde, hasta)
    rows = _list_incidencias_rows(db, start_date, end_date)
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["id", "fecha_detectada", "modulo", "titulo", "severidad", "estatus", "responsable", "detalle", "resuelta_at"])
    for row in rows:
        writer.writerow(
            [
                row.id,
                row.fecha_detectada.isoformat(),
                row.modulo,
                row.titulo,
                row.severidad.value,
                row.estatus.value,
                row.responsable or "",
                row.detalle or "",
                row.resuelta_at.isoformat() if row.resuelta_at else "",
            ]
        )
    filename = f"direccion_incidencias_{start_date.isoformat()}_{end_date.isoformat()}.csv"
    return Response(
        content=buf.getvalue(),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/export/acciones.csv", summary="Exportar acciones semanales de dirección a CSV")
def export_acciones_csv(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user_jwt),
    week_start: date | None = Query(default=None),
    week_end: date | None = Query(default=None),
) -> Response:
    _require_direccion_or_admin(user)
    start_date, end_date = _clamp_range(week_start, week_end)
    rows = _list_acciones_rows(db, start_date, end_date)
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["id", "week_start", "week_end", "titulo", "owner", "due_date", "estatus", "impacto", "descripcion"])
    for row in rows:
        writer.writerow(
            [
                row.id,
                row.week_start.isoformat(),
                row.week_end.isoformat(),
                row.titulo,
                row.owner,
                row.due_date.isoformat() if row.due_date else "",
                row.estatus.value,
                row.impacto or "",
                row.descripcion or "",
            ]
        )
    filename = f"direccion_acciones_{start_date.isoformat()}_{end_date.isoformat()}.csv"
    return Response(
        content=buf.getvalue(),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/export/reportes-completo.csv", summary="Exportar sistema integral de reportes a CSV")
def export_reporte_completo_csv(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user_jwt),
    desde: date | None = Query(default=None),
    hasta: date | None = Query(default=None),
) -> Response:
    _require_direccion_or_admin(user)
    start_date, end_date = _clamp_range(desde, hasta)
    reporte = _build_reporte_completo(db=db, user=user, start_date=start_date, end_date=end_date)
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["seccion", "kpi", "valor"])
    writer.writerow(["periodo", "desde", reporte.desde.isoformat()])
    writer.writerow(["periodo", "hasta", reporte.hasta.isoformat()])
    for key, value in reporte.financiero.model_dump().items():
        writer.writerow(["financiero", key, value])
    for key, value in reporte.conversion.model_dump().items():
        writer.writerow(["conversion", key, value])
    cartera_data = reporte.cartera.model_dump()
    antiguedad = cartera_data.pop("antiguedad", [])
    for key, value in cartera_data.items():
        writer.writerow(["cartera", key, value])
    for item in antiguedad:
        writer.writerow(["cartera_antiguedad", item["bucket"], f"{item['monto']} ({item['facturas']} facturas)"])
    for key, value in reporte.productividad.model_dump().items():
        writer.writerow(["productividad", key, value])
    writer.writerow(["sostenibilidad", "estado", reporte.sostenibilidad.estado])
    writer.writerow(["sostenibilidad", "mensaje", reporte.sostenibilidad.mensaje])
    for idx, alerta in enumerate(reporte.sostenibilidad.alertas, start=1):
        writer.writerow(["sostenibilidad_alerta", f"alerta_{idx}", alerta])
    for key, value in reporte.sostenibilidad.semaforo.model_dump().items():
        writer.writerow(["semaforo", key, value])
    for idx, item in enumerate(reporte.top_clientes_rentabilidad, start=1):
        data = item.model_dump()
        for key, value in data.items():
            writer.writerow([f"top_clientes_{idx}", key, value])
    guardrails = reporte.decision_guardrails
    if guardrails is not None:
        writer.writerow(["guardrails", "bloqueado", guardrails.bloqueado])
        for idx, reason in enumerate(guardrails.motivos_bloqueo, start=1):
            writer.writerow(["guardrails_bloqueo", f"motivo_{idx}", reason])
        for idx, action in enumerate(guardrails.acciones_recomendadas, start=1):
            writer.writerow(["guardrails_accion", f"accion_{idx}", action])
        for idx, item in enumerate(guardrails.items, start=1):
            row = item.model_dump()
            for key, value in row.items():
                writer.writerow([f"guardrails_item_{idx}", key, value])
    filename = f"direccion_reporte_completo_{start_date.isoformat()}_{end_date.isoformat()}.csv"
    return Response(
        content=buf.getvalue(),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
