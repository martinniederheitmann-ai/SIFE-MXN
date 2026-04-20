from __future__ import annotations

import csv
import io
from datetime import date, datetime, time, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user_jwt, get_db
from app.models.asignacion import Asignacion
from app.models.despacho import Despacho, DespachoEvento, EstadoDespacho, TipoEventoDespacho
from app.models.direccion import (
    AccionEstatus,
    DireccionAccion,
    DireccionIncidencia,
    IncidenciaEstatus,
    IncidenciaSeveridad,
)
from app.models.factura import EstatusFactura, Factura
from app.models.flete import Flete
from app.models.orden_servicio import OrdenServicio
from app.models.user import User
from app.schemas.direccion import (
    DireccionAccionCreate,
    DireccionAccionRead,
    DireccionAccionUpdate,
    DireccionDashboardResponse,
    DireccionEmbudo,
    DireccionIncidenciaCreate,
    DireccionIncidenciaRead,
    DireccionIncidenciaUpdate,
    DireccionKpiResumen,
    DireccionSemaforo,
    DireccionTiemposCiclo,
)

router = APIRouter()


def _require_direccion_or_admin(user: User) -> None:
    role = (user.role.name if user.role else "").strip().lower()
    if role not in {"admin", "direccion"}:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo admin o direccion pueden consultar el tablero de direccion.",
        )


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
    return _incidencia_to_read(row)


@router.patch("/incidencias/{incidencia_id}", response_model=DireccionIncidenciaRead, summary="Actualizar incidencia dirección")
def update_incidencia(
    incidencia_id: int,
    payload: DireccionIncidenciaUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user_jwt),
) -> DireccionIncidenciaRead:
    _require_direccion_or_admin(user)
    row = db.get(DireccionIncidencia, incidencia_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Incidencia no encontrada.")
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
    return _accion_to_read(row)


@router.patch("/acciones/{accion_id}", response_model=DireccionAccionRead, summary="Actualizar acción semanal dirección")
def update_accion(
    accion_id: int,
    payload: DireccionAccionUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user_jwt),
) -> DireccionAccionRead:
    _require_direccion_or_admin(user)
    row = db.get(DireccionAccion, accion_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Accion no encontrada.")
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
    return _accion_to_read(row)


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
        },
        "semaforo": dashboard.semaforo.model_dump(),
        "embudo": dashboard.embudo.model_dump(),
        "tiempos": dashboard.tiempos.model_dump(),
    }


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
