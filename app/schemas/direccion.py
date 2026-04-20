from __future__ import annotations

from datetime import date

from pydantic import BaseModel


class DireccionKpiResumen(BaseModel):
    fletes: int
    ordenes_servicio: int
    asignaciones: int
    despachos: int
    despachos_cerrados: int
    facturas: int
    facturas_emitidas: int
    incidencias_despacho: int


class DireccionEmbudo(BaseModel):
    fletes_a_os_pct: float
    os_a_asignacion_pct: float
    asignacion_a_despacho_pct: float
    despacho_a_factura_pct: float


class DireccionTiemposCiclo(BaseModel):
    flete_a_factura_horas: float | None = None
    orden_a_despacho_horas: float | None = None
    despacho_a_factura_horas: float | None = None


class DireccionSemaforo(BaseModel):
    operacion: str
    sistema: str
    dato: str
    cobranza: str


class DireccionDashboardResponse(BaseModel):
    desde: date
    hasta: date
    resumen: DireccionKpiResumen
    embudo: DireccionEmbudo
    tiempos: DireccionTiemposCiclo
    semaforo: DireccionSemaforo
